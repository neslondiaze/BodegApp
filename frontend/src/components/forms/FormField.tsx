import { useId, type InputHTMLAttributes, type ReactNode, type SelectHTMLAttributes } from 'react';

/**
 * Reusable form field primitives (design system §5.2):
 * visible label above the input (never placeholder-only), helper text
 * in text-secondary, error message with role="alert" 4px under the field.
 * Errors are communicated by text, not color alone (a11y §7.3 rule 5).
 */

interface FieldMessagesProps {
  error?: string | null;
  helper?: string;
  describedBy?: string;
}

function FieldMessages({ error, helper, describedBy }: FieldMessagesProps) {
  if (!error && !helper) return null;
  return (
    <div id={describedBy} className="mt-1 text-xs">
      {error ? (
        <p role="alert" className="font-medium text-primary">
          {error}
        </p>
      ) : (
        <p className="text-content-muted">{helper}</p>
      )}
    </div>
  );
}

interface BaseFieldProps {
  label: string;
  error?: string | null;
  helper?: string;
}

interface TextFieldProps extends BaseFieldProps, InputHTMLAttributes<HTMLInputElement> {}

interface SelectFieldProps extends BaseFieldProps, SelectHTMLAttributes<HTMLSelectElement> {
  children: ReactNode;
}

/** Text input with label + error + helper wiring (a11y: aria-describedby, aria-invalid). */
export function TextField({ label, error, helper, ...inputProps }: TextFieldProps) {
  const autoId = useId();
  const id = inputProps.id ?? autoId;
  const describedBy = `${id}-messages`;
  const hasMessages = Boolean(error ?? helper);

  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-content-base">
        {label}
      </label>
      <input
        {...inputProps}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={hasMessages ? describedBy : undefined}
        className={`w-full rounded-lg border bg-surface px-3 py-2.5 text-sm text-content-base placeholder:text-content-muted focus:border-primary focus:outline-none ${
          error ? 'border-primary' : 'border-border-subtle'
        }`}
      />
      <FieldMessages error={error} helper={helper} describedBy={describedBy} />
    </div>
  );
}

/** Select with the same label/error/helper contract as TextField. */
export function SelectField({ label, error, helper, children, ...selectProps }: SelectFieldProps) {
  const autoId = useId();
  const id = selectProps.id ?? autoId;
  const describedBy = `${id}-messages`;
  const hasMessages = Boolean(error ?? helper);

  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-content-base">
        {label}
      </label>
      <select
        {...selectProps}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={hasMessages ? describedBy : undefined}
        className={`w-full rounded-lg border bg-surface px-3 py-2.5 text-sm text-content-base focus:border-primary focus:outline-none ${
          error ? 'border-primary' : 'border-border-subtle'
        }`}
      >
        {children}
      </select>
      <FieldMessages error={error} helper={helper} describedBy={describedBy} />
    </div>
  );
}
