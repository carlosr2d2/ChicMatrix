type StyleChip = {
  code: string;
  label?: string;
  score?: number;
};

type StyleChipsProps = {
  tags: StyleChip[];
  className?: string;
};

export function StyleChips({ tags, className = "" }: StyleChipsProps) {
  if (!tags.length) return null;

  return (
    <ul className={`flex flex-wrap gap-1.5 ${className}`.trim()} aria-label="Estilos">
      {tags.map((tag) => (
        <li
          key={tag.code}
          className="text-[10px] tracking-[0.15em] uppercase text-stone-600 border border-sand/90 bg-cream/80 px-2 py-0.5"
        >
          {tag.label ?? tag.code}
          {typeof tag.score === "number" ? (
            <span className="ml-1 text-stone-400 normal-case tracking-normal">
              {tag.score.toFixed(1)}
            </span>
          ) : null}
        </li>
      ))}
    </ul>
  );
}
