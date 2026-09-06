import { useId, type ReactNode } from 'react';

/**
 * Alert banners (design system §5.6): flat tinted surface + 4px
 * colored left border. Body text always uses content-base so the
 * contrast matrix from §7 holds in both themes; the semantic color
 * is carried by the border, never by the text alone (a11y).
 */

type AlertVariant = 'success' | 'error' | 'info' | 'warning';

const VARIANT_CLASSES: Record<AlertVariant, string> = {
  success: 'border-accent',
  error: 'border-primary-deep',
  info: 'border-border-subtle',
  warning: 'border-secondary',
};

const VARIANT_BG: Record<AlertVariant, string> = {
  success: 'bg-accent/10',
  error: 'bg-primary/10',
  info: 'bg-primary/5',
  warning: 'bg-secondary/15',
};

interface AlertProps {
  variant: AlertVariant;
  children: ReactNode;
  onDismiss?: () => void;
  dismissLabel?: string;
}

export function Alert({ variant, children, onDismiss, dismissLabel = 'Cerrar alerta' }: AlertProps) {
  const titleId = useId();
  return (
    <div
      role={variant === 'error' ? 'alert' : 'status'}
      aria-labelledby={titleId}
      className={`rounded-lg border-l-4 ${VARIANT_BG[variant]} ${VARIANT_CLASSES[variant]} px-4 py-3`}
    >
      <div className="flex items-start justify-between gap-3">
        <div id={titleId} className="text-sm text-content-base">
          {children}
        </div>
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            aria-label={dismissLabel}
            className="shrink-0 rounded-md p-1 text-content-muted transition-colors hover:text-content-base focus:outline-none"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M6 6l12 12M18 6L6 18"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
