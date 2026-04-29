type MetricCardProps = {
  label: string;
  value: string;
  tone?: "light" | "dark";
};

export function MetricCard({ label, value, tone = "light" }: MetricCardProps) {
  return (
    <div
      className={
        tone === "dark"
          ? "rounded-xl border border-white/10 bg-white/[0.08] p-5 text-white"
          : "rounded-xl border border-line bg-white/70 p-5 text-primary"
      }
    >
      <p className={tone === "dark" ? "text-sm text-white/[0.58]" : "text-sm text-muted"}>
        {label}
      </p>
      <p className="mt-2 font-serif text-3xl font-semibold">{value}</p>
    </div>
  );
}
