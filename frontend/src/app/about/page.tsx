import { CheckCircle2, Leaf, Sparkles, UsersRound } from "lucide-react";
import { PageHero } from "@/components/PageHero";
import { SectionHeader } from "@/components/SectionHeader";

const values = [
  "Make AI useful for everyday farming decisions.",
  "Bridge traditional field knowledge with model-backed recommendations.",
  "Keep the interface clean enough for farmers and deep enough for agronomists.",
];

export default function AboutPage() {
  return (
    <>
      <PageHero
        eyebrow="About AgroSense"
        title="AI for farmers, built with clarity and trust."
        description="AgroSense combines crop science, machine learning, and practical advisory workflows into a premium smart farming platform."
        image="https://images.unsplash.com/photo-1499529112087-3cb3b73cec95?auto=format&fit=crop&w=1800&q=80"
      />
      <section className="page-band bg-cream">
        <div className="container-frame grid gap-10 lg:grid-cols-[0.85fr_1fr] lg:items-center">
          <SectionHeader
            eyebrow="Mission"
            title="Help farmers make better decisions before problems become losses."
            description="The MVP focuses on the four highest-value intelligence flows: crop choice, disease response, fertilizer planning, and advisory support."
          />
          <div className="grid gap-4">
            {values.map((value) => (
              <div key={value} className="flex gap-3 rounded-2xl border border-line bg-white/[0.76] p-5">
                <CheckCircle2 className="mt-1 size-5 shrink-0 text-earth" />
                <p className="font-semibold leading-7 text-primary">{value}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="page-band bg-background">
        <div className="container-frame grid gap-5 md:grid-cols-3">
          {[
            {
              icon: Leaf,
              title: "Why AgroSense",
              text: "Farmers need fast answers across soil, crop, disease, and nutrient decisions without switching between disconnected tools.",
            },
            {
              icon: Sparkles,
              title: "AI for farmers story",
              text: "The platform turns trained models and advisory intelligence into simple workflows that can be used at the edge of the field.",
            },
            {
              icon: UsersRound,
              title: "Team vision",
              text: "Build a scalable agri-tech ecosystem that stays warm, practical, and trustworthy as more intelligence layers are added.",
            },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.title} className="rounded-2xl border border-line bg-white/[0.76] p-6">
                <span className="mb-5 grid size-12 place-items-center rounded-xl bg-mint text-primary">
                  <Icon className="size-5" />
                </span>
                <h2 className="font-serif text-2xl font-semibold text-primary">
                  {item.title}
                </h2>
                <p className="mt-3 text-sm leading-6 text-muted">{item.text}</p>
              </article>
            );
          })}
        </div>
      </section>
    </>
  );
}
