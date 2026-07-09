type SpinnerProps = {
  label?: string;
  className?: string;
};

export function Spinner({ label = "Loading", className = "" }: SpinnerProps) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`} role="status" aria-live="polite">
      <span
        className="h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent"
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
      {label ? <span className="text-sm">{label}</span> : null}
    </span>
  );
}
