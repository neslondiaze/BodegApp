import type { Config } from 'tailwindcss';

/*
 * BodegApp design tokens — investor-mandated palette (docs/REQUERIMIENTOS.md §4).
 * Light: Primario #C41230 (deep variant #800020), Secundario #FFB81C,
 *         Acento #2E7D32, Fondo #F8F9FA, Texto #212529 / #6C757D.
 * Dark:  Fondo #121212, Tarjetas #1E1E1E, Primario #E53935, Secundario #FFCA28,
 *         Acento #81C784, Texto #FFFFFF / #E0E0E0, Secundario #9E9E9E, Bordes #2C2C2C.
 */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          light: 'var(--surface-light)',
          dark: 'var(--surface-dark)',
          DEFAULT: 'var(--surface)',
          card: 'var(--surface-card)',
        },
        primary: {
          light: '#C41230',
          deep: '#800020',
          dark: '#E53935',
          DEFAULT: 'var(--color-primary)',
          foreground: 'var(--color-primary-foreground)',
        },
        secondary: {
          light: '#FFB81C',
          dark: '#FFCA28',
          DEFAULT: 'var(--color-secondary)',
        },
        accent: {
          light: '#2E7D32',
          dark: '#81C784',
          DEFAULT: 'var(--color-accent)',
        },
        content: {
          base: 'var(--content-base)',
          muted: 'var(--content-muted)',
        },
        border: {
          subtle: 'var(--border-subtle)',
        },
      },
      fontFamily: {
        headline: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
