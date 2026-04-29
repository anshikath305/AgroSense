type SectionHeaderProps = {
  eyebrow: string;
  title: string;
  description?: string;
  align?: "left" | "center";
};

export function SectionHeader({
  eyebrow,
  title,
  description,
  align = "left",
}: SectionHeaderProps) {
  return (
    <div className={align === "center" ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}>
      <p className="mb-3 text-xs font-bold uppercase tracking-widest text-earth">
        {eyebrow}
      </p>
      <h2 className="font-serif text-4xl font-semibold text-primary md:text-5xl">
        {title}
      </h2>
      {description ? (
        <p className="mt-5 text-base leading-7 text-muted md:text-lg">
          {description}
        </p>
      ) : null}
    </div>
  );
}
