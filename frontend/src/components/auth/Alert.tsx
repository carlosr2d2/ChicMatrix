type AlertProps = {
  variant: "success" | "error" | "info";
  title?: string;
  children: React.ReactNode;
};

const variantStyles = {
  success: "border-green-200 bg-green-50 text-green-900",
  error: "border-red-200 bg-red-50 text-red-900",
  info: "border-sand bg-white text-stone-700",
};

export function Alert({ variant, title, children }: AlertProps) {
  return (
    <div
      role={variant === "error" ? "alert" : "status"}
      aria-live="polite"
      className={`rounded-sm border px-4 py-3 text-sm animate-fade-in ${variantStyles[variant]}`}
    >
      {title ? <p className="mb-1 font-medium">{title}</p> : null}
      <div className="font-light leading-relaxed">{children}</div>
    </div>
  );
}
