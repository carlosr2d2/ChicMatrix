type ConsentCheckboxProps = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  error?: string | null;
};

export function ConsentCheckbox({ checked, onChange, error }: ConsentCheckboxProps) {
  return (
    <div>
      <label className="flex items-start gap-3 text-sm text-stone-600 cursor-pointer">
        <input
          type="checkbox"
          checked={checked}
          onChange={(event) => onChange(event.target.checked)}
          className="mt-1 h-4 w-4 rounded border-sand text-ink focus:ring-ink"
          aria-invalid={Boolean(error)}
          aria-describedby={error ? "consent-error" : undefined}
        />
        <span className="font-light leading-relaxed">
          I consent to the processing of my personal data under GDPR / Habeas Data regulations.
        </span>
      </label>
      {error ? (
        <p id="consent-error" className="mt-2 text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
