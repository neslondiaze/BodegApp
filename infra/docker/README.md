# BodegApp — Infraestructura Docker (Sentinel Shield v1.0)

> Tarea F0-02 | Responsable: Alfredo (DevOps) | Revisión de seguridad: Lead_Blue (F0-07)
> Referencia: `docs/REQUERIMIENTOS.md` req 0-4.

Despliegue endurecido de BodegApp con Docker Compose bajo el modelo Zero Trust. Este README describe la arquitectura de red, la gestión de secrets y los pasos de despliegue.

## Arquitectura Zero Trust

```
                Internet / LAN
                      |
              [host :80 / :443]
                      |
                 ┌────┴─────┐
                 │  proxy   │  nginx inversor (única entrada, TLS)
                 └─┬─────┬──┘
        frontend-seg│     │api-seg
              ┌─────┴──┐  ┌──┴─────┐
              │frontend│  │  api   │  FastAPI
              └────────┘  └──┬─────┘
                       db-seg│
                      ┌──────┴──┐
                      │postgres │
                      └─────────┘
```

- **Cuatro redes segmentadas** (`edge`, `frontend-seg`, `api-seg`, `db-seg`). Cada servicio se une únicamente a las redes que necesita.
- **Solo el proxy publica puertos** al host (80/443). Ni la API, ni el frontend, ni PostgreSQL exponen puertos directos. No se usa `network_mode: host` en ningún servicio.
- **Las redes internas son `internal: true`**: no tienen ruta hacia el exterior, lo que corta rutas de movimiento lateral y exfiltración.
- **PostgreSQL solo es alcanzable por la API** (segmento `db-seg`); el proxy no tiene ruta a la base de datos.

## Endurecimiento por contenedor

| Control | Valor |
|---|---|
| Usuario | Procesos que sirven tráfico no-root en los 4 servicios: workers nginx uid 101, uvicorn uid 65532 (vía `setpriv`), postgres uid 999 (vía gosu oficial) |
| Capacidades | `cap_drop: ALL` + caps mínimas documentadas por servicio (proxy/api: CHOWN, SETGID, SETUID, DAC_READ_SEARCH; postgres agrega DAC_OVERRIDE y FOWNER; frontend: cero caps) |
| `security_opt` | `no-new-privileges:true` en todos |
| Sistema de archivos | `read_only: true` + `tmpfs` en las rutas de escritura (con `uid=`/`gid=` donde el proceso es no-root) |
| Healthchecks | En los 4 servicios |
| Límites de recursos | `cpus`/`memory`/`pids` (límites y reservas) por servicio |
| Otros | `pids_limit`, `init: true`, `ulimits.nofile`, logging rotativo (`max-size 10m`, 3 archivos), políticas de reinicio `unless-stopped` |

### Modelo de privilegios y secrets (patrón stage-and-drop)

Docker Compose sin swarm monta los secrets file-based **con el ownership del host (root, 0600)** — las opciones `uid`/`gid`/`mode` de la definición del secret se ignoran fuera de swarm (verificado empíricamente). Por eso los servicios que consumen secrets usan el patrón **stage-and-drop**:

1. El contenedor arranca como root **solo** para leer los secrets (con `cap_add` mínimas: `CHOWN`, `DAC_READ_SEARCH`, `SETGID`, `SETUID`).
2. Copia los secrets a `/tmp/keys` (tmpfs efímero) con ownership del usuario de la app.
3. Ejecuta `setpriv --reuid --regid --init-groups --no-new-privs` (o `gosu` en postgres, `user nginx;` en el proxy) y el proceso que sirve tráfico corre no-root.

Los valores de los secrets NUNCA aparecen en variables de entorno: solo rutas de archivo (`*_FILE`).

## Secrets de Docker

El material sensible **nunca** viaja en variables de entorno en texto plano ni dentro de las imágenes. Se usa **Docker secrets** con el convenio `*_FILE`:

| Secret | Uso | Consumidor |
|---|---|---|
| `postgres_password` | Contraseña de PostgreSQL (SCRAM-SHA-256) | `postgres`, `api` |
| `jwt_private_key` | Clave privada RS256 para firmar tokens | `api` |
| `jwt_public_key` | Clave pública RS256 para verificar tokens | `api` |
| `proxy_tls_cert` / `proxy_tls_key` | Certificado y clave del proxy (TLS en el borde) | `proxy` |

Los archivos de secrets viven en `infra/docker/secrets/` (excluidos de git con `.gitignore`). En producción deben provisionarse desde un gestor de secrets (Vault, SOPS, etc.) antes del despliegue.

## Pasos de despliegue

### 1. Generación de secrets

```bash
cd infra/docker
mkdir -p secrets

# Contraseña de PostgreSQL (guárdala en tu gestor de contraseñas)
openssl rand -base64 32 > secrets/postgres_password.txt

# Par de claves JWT RS256 (4096 bits)
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out secrets/jwt_private_key.pem
openssl pkey -in secrets/jwt_private_key.pem -pubout -out secrets/jwt_public_key.pem
chmod 600 secrets/jwt_private_key.pem

# Certificado TLS autofirmado para desarrollo
# (en producción usa un certificado de tu CA interna o LetsEncrypt)
openssl req -x509 -nodes -newkey rsa:4096 -sha256 -days 365 \
  -keyout secrets/proxy_tls_key.pem -out secrets/proxy_tls_cert.pem \
  -subj "/CN=bodegapp.local" \
  -addext "subjectAltName=DNS:bodegapp.local,DNS:localhost,IP:127.0.0.1"
chmod 600 secrets/proxy_tls_key.pem
```

### 2. Variables de entorno

```bash
cp .env.example .env
# Ajusta valores no sensibles si lo necesitas
```

### 3. Levantar la plataforma

```bash
docker compose up -d --build
```

### 4. Verificación

```bash
docker compose ps                          # los 4 servicios deben quedar healthy
docker compose logs -f proxy               # revisa TLS y upstreams
curl -k https://localhost/healthz           # debe devolver ok
curl -k https://localhost/api/health        # debe responder la API
```

### 5. Operación

```bash
docker compose down                        # detener (los datos de postgres persisten en el volumen)
docker compose down -v                    # ADVERTENCIA: elimina también los datos de la base de datos
```

## Contratos de build con otros equipos

- **Backend (Nelson, F0-03/F0-04)**: el contexto de build es `backend/`. Se espera `backend/app/main.py` con el objeto ASGI `app` (i.e. `app.main:app`), `backend/requirements.txt` con versiones fijadas y el endpoint `GET /health` (200). La configuración sensible se lee con el convenio `*_FILE` apuntando a `/run/secrets/`.
- **Frontend (Noris, F0-05)**: el contexto de build es `frontend/`. Se espera `frontend/package.json` con un script `build` (Vite) que genere `frontend/dist/`. El valor `VITE_API_BASE_URL` se pasa como build arg (todo lo compilado por Vite es público: nunca incluir secrets ahí).
- El `nginx.conf` del frontend se hornea dentro de la imagen (contexto adicional `docker:`) para que el contenedor sea inmutable en ejecución.

## Notas para Lead_Blue (auditoría F0-07)

- Los archivos de secrets en `infra/docker/secrets/` están fuera de git (`.gitignore`). Se generan localmente con los comandos de este README; en producción deben provisionarse desde un gestor de secrets antes del despliegue.
- HSTS se emite solo por el proxy en respuestas TLS; no se incluye `preload` a la espera de confirmar la política de dominio (evita bloquear el dominio antes de que HTTPS sea 100% estable).
- CSP permite `style-src 'unsafe-inline'` temporalmente para compatibilidad con estilos inline de React 19/Tailwind; se recomienda sustituirlo por nonces/hash cuando el frontend esté maduro (F4-02).
- `connect-src 'self'` en CSP: el frontend debe llamar a la API por el mismo origen (`/api`) — ya cubierto por `VITE_API_BASE_URL=/api`.
- Los certificados autofirmados de desarrollo son solo para desarrollo; producción requiere una CA válida (LetsEncrypt o CA interna del cliente).
- Los masters de nginx/postgres/api arrancan como root solo para leer secrets root-owned (patrón stage-and-drop documentado arriba); todos los procesos que sirven tráfico (workers, uvicorn, engine postgres) son no-root. El frontend corre 100% no-root sin caps.
- Limitación conocida de Compose no-swarm: `uid`/`gid`/`mode` de los secrets se ignoran (los archivos montan root 0600). El patrón stage-and-drop la neutraliza; en swarm/k8s esos atributos sí aplican.
- Imagen postgres fijada a `postgres:16-alpine` (mayor versionada). Para fijar el patch exacto (p. ej. `16.9-alpine`) cuando el registry esté accesible, verificar que la variante alpine exista para ese patch.

## Estructura

```
infra/docker/
├── docker-compose.yml      # definición de servicios endurecida (Zero Trust)
├── Dockerfile.api          # multi-stage python:3.12-slim, stage-and-drop a appuser
├── Dockerfile.frontend     # multi-stage node -> nginx, non-root, cero caps
├── .env.example            # solo variables NO sensibles
├── .gitignore              # excluye secrets/ y .env
├── frontend/
│   ├── nginx.conf          # server block del SPA (horneado en imagen)
│   └── nginx-main.conf    # main conf con pid en /tmp (horneado en imagen)
├── proxy/
│   ├── nginx.conf          # proxy inversor TLS (montado read-only)
│   └── nginx-main.conf     # main conf con pid en /tmp (montado read-only)
└── secrets/                # NO está en git — generado localmente
    ├── postgres_password.txt
    ├── jwt_private_key.pem
    ├── jwt_public_key.pem
    ├── proxy_tls_cert.pem
    └── proxy_tls_key.pem
```
