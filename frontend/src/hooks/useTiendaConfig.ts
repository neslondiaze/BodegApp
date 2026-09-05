import { useCallback, useEffect, useRef, useState } from 'react';
import { tiendaApi, toApiError, type ApiErrorLike } from '@/lib/tiendaApi';
import type { StoreConfig } from '@/types/tienda';

/**
 * useTiendaConfig — data-fetching hook for the store configuration
 * screen (M-01). Loads the config on mount (404 = "never saved" create
 * mode), exposes a save() that PUTs the whole form, and surfaces
 * loading / saving / success / error states to the page.
 *
 * The request-in-flight guard prevents state updates after unmount or
 * from superseded requests (the pattern AuthContext uses via sessionRef).
 */
export function useTiendaConfig() {
  const [config, setConfig] = useState<StoreConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [loadError, setLoadError] = useState<ApiErrorLike | null>(null);
  const [saveError, setSaveError] = useState<ApiErrorLike | null>(null);
  const requestRef = useRef(0);

  useEffect(() => {
    const request = ++requestRef.current;
    let active = true;

    (async () => {
      try {
        const data = await tiendaApi.getConfig();
        if (active && request === requestRef.current) {
          setConfig(data);
          setIsLoading(false);
        }
      } catch (error) {
        const apiError = toApiError(error);
        if (active && request === requestRef.current) {
          // 404 RECURSO_NO_ENCONTRADO: the tenant never saved a config —
          // start in create mode with an empty form, not as a failure.
          if (apiError.status === 404) {
            setConfig(null);
            setIsLoading(false);
          } else {
            setLoadError(apiError);
            setIsLoading(false);
          }
        }
      }
    })();

    return () => {
      active = false;
    };
  }, []);

  const save = useCallback(async (payload: Parameters<typeof tiendaApi.updateConfig>[0]) => {
    const request = ++requestRef.current;
    setIsSaving(true);
    setSaveError(null);
    setIsSuccess(false);
    try {
      const data = await tiendaApi.updateConfig(payload);
      if (request === requestRef.current) {
        setConfig(data);
        setIsSuccess(true);
      }
      return data;
    } catch (error) {
      const apiError = toApiError(error);
      if (request === requestRef.current) {
        setSaveError(apiError);
      }
      throw apiError;
    } finally {
      if (request === requestRef.current) {
        setIsSaving(false);
      }
    }
  }, []);

  const dismissSuccess = useCallback(() => setIsSuccess(false), []);

  return {
    config,
    isLoading,
    isSaving,
    isSuccess,
    loadError,
    saveError,
    save,
    dismissSuccess,
  } as const;
}
