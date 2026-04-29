import Link from "next/link";
import Image from "next/image";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { HeroDashboard } from "@/components/HeroDashboard";
import { MetricCard } from "@/components/MetricCard";
import { SectionHeader } from "@/components/SectionHeader";
import { benefits, features, howItWorks, testimonials } from "@/lib/content";

export default function Home() {
  return (
    <>
      <section className="relative isolate overflow-hidden bg-primary text-white">
        <Image
          src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=80"
          alt="Wide green crop field under a clear sky"
          fill
          priority
          sizes="100vw"
          className="-z-20 object-cover"
        />
        <div className="absolute inset-0 -z-10 bg-primary/[0.68]" />
        <div className="container-frame grid min-h-[calc(100svh-80px)] items-center gap-12 py-14 lg:grid-cols-[1fr_0.82fr]">
          <div className="max-w-3xl">
            <p className="mb-5 inline-flex rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-bold uppercase tracking-widest text-gold backdrop-blur-xl">
              MVP v1 Web Platform
            </p>
            <h1 className="font-serif text-6xl font-semibold leading-none md:text-7xl">
              AgroSense
            </h1>
            <p className="mt-6 max-w-2xl text-xl leading-8 text-mint">
              AI powered crop recommendation, disease detection, fertilizer
              prediction, and farming advisory in one clean platform.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/crop-ai"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-gold px-6 py-4 text-sm font-bold text-primary transition hover:brightness-105"
              >
                Try Crop AI
                <ArrowRight className="size-4" />
              </Link>
              <Link
                href="/assistant"
                className="inline-flex items-center justify-center rounded-xl border border-white/25 bg-white/10 px-6 py-4 text-sm font-bold text-white backdrop-blur-xl transition hover:bg-white/[0.16]"
              >
                Ask Assistant
              </Link>
            </div>
          </div>
          <div className="pb-8 lg:pb-0">
            <HeroDashboard />
          </div>
        </div>
      </section>

      <section id="features" className="page-band bg-cream">
        <div className="container-frame">
          <SectionHeader
            eyebrow="Core AI tools"
            title="Four focused workflows for smarter farming"
            description="Each feature is built around a real farmer decision: what to grow, what is wrong, what to apply, and what to do next."
            align="center"
          />
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <Link
                  key={feature.title}
                  href={feature.href}
                  className="group rounded-2xl border border-line bg-white/[0.76] p-6 shadow-sm transition hover:-translate-y-1 hover:border-sage hover:shadow-xl hover:shadow-primary/5"
                >
                  <span className="mb-5 grid size-12 place-items-center rounded-xl bg-mint text-primary">
                    <Icon className="size-5" />
                  </span>
                  <h3 className="font-serif text-2xl font-semibold text-primary">
                    {feature.title}
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-muted">
                    {feature.description}
                  </p>
                  <span className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-earth">
                    Open tool
                    <ArrowRight className="size-4 transition group-hover:translate-x-1" />
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      <section className="page-band bg-background">
        <div className="container-frame grid gap-12 lg:grid-cols-[0.86fr_1fr] lg:items-center">
          <SectionHeader
            eyebrow="How it works"
            title="From field input to model-backed recommendation"
            description="AgroSense keeps the workflow simple while routing each request to the right model service behind the scenes."
          />
          <div className="grid gap-4">
            {howItWorks.map((step, index) => (
              <div
                key={step}
                className="flex gap-4 rounded-2xl border border-line bg-white/[0.74] p-5"
              >
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-primary text-gold">
                  {index + 1}
                </span>
                <p className="pt-2 font-semibold text-primary">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-primary py-16 text-white">
        <div className="container-frame grid gap-4 md:grid-cols-4">
          {benefits.map((item) => (
            <MetricCard
              key={item.label}
              label={item.label}
              value={item.metric}
              tone="dark"
            />
          ))}
        </div>
      </section>

      <section className="page-band bg-cream">
        <div className="container-frame">
          <SectionHeader
            eyebrow="Farmer focused"
            title="Clear answers without clutter"
            description="The MVP removes filler, duplicate sections, and unrelated features so farmers can act quickly."
            align="center"
          />
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {testimonials.map((item) => (
              <article
                key={item.name}
                className="rounded-2xl border border-line bg-white/[0.76] p-6"
              >
                <p className="text-base leading-7 text-primary">
                  &quot;{item.quote}&quot;
                </p>
                <div className="mt-6 border-t border-line pt-5">
                  <p className="font-bold text-primary">{item.name}</p>
                  <p className="text-sm text-muted">{item.role}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="page-band bg-background">
        <div className="container-frame overflow-hidden rounded-3xl bg-primary p-8 text-white md:p-12">
          <div className="grid gap-10 lg:grid-cols-[1fr_0.8fr] lg:items-center">
            <div>
              <p className="mb-4 text-xs font-bold uppercase tracking-widest text-gold">
                Ready for MVP demos
              </p>
              <h2 className="font-serif text-4xl font-semibold md:text-5xl">
                Start with one field decision today.
              </h2>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-mint">
                Use Crop AI, scan a leaf, plan fertilizer, or ask the assistant.
                Every page follows the same polished AgroSense system.
              </p>
            </div>
            <div className="grid gap-3">
              {[
                "Unified visual design",
                "Model-backed API routes",
                "No IoT integration in MVP",
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-3 rounded-xl bg-white/10 p-4"
                >
                  <CheckCircle2 className="size-5 text-gold" />
                  <span className="font-semibold">{item}</span>
                </div>
              ))}
              <Link
                href="/disease-ai"
                className="mt-2 inline-flex items-center justify-center rounded-xl bg-gold px-6 py-4 text-sm font-bold text-primary"
              >
                Try Disease AI
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
