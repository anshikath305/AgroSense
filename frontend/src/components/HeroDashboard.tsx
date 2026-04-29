"use client";

import { motion } from "framer-motion";
import { Activity, Droplets, FlaskConical, Leaf, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { heroStats } from "@/lib/content";

const readinessMetrics: { label: string; value: number; icon: LucideIcon }[] = [
  { label: "Nutrient balance", value: 82, icon: FlaskConical },
  { label: "Moisture profile", value: 68, icon: Droplets },
  { label: "Crop suitability", value: 91, icon: Leaf },
];

export function HeroDashboard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.15 }}
      className="glass-panel-dark w-full max-w-xl rounded-2xl p-5 text-white shadow-2xl shadow-primary/30"
    >
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-gold">
            Farm Intelligence
          </p>
          <h2 className="mt-1 font-serif text-2xl font-semibold">
            Live recommendation board
          </h2>
        </div>
        <span className="grid size-11 place-items-center rounded-xl bg-white/10 text-gold">
          <Sparkles className="size-5" />
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {heroStats.map((item, index) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.25 + index * 0.12 }}
              className="rounded-xl border border-white/10 bg-white/[0.08] p-4"
            >
              <Icon className="mb-3 size-5 text-gold" />
              <p className="text-xs text-white/[0.58]">{item.label}</p>
              <p className="mt-1 text-sm font-bold">{item.value}</p>
            </motion.div>
          );
        })}
      </div>

      <div className="mt-4 rounded-xl border border-white/10 bg-white/[0.08] p-4">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm font-semibold text-white/[0.72]">Field readiness</span>
          <span className="rounded-full bg-gold px-3 py-1 text-xs font-bold text-primary">
            91% match
          </span>
        </div>
        <div className="space-y-3">
          {readinessMetrics.map(({ label, value, icon: Icon }) => (
            <div key={label}>
              <div className="mb-1 flex items-center justify-between text-xs text-white/[0.62]">
                <span className="flex items-center gap-2">
                  <Icon className="size-3.5" />
                  {label}
                </span>
                <span>{value}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-white/[0.12]">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${value}%` }}
                  transition={{ duration: 0.9, delay: 0.35 }}
                  className="h-full rounded-full bg-gold"
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 flex items-start gap-3 rounded-xl border border-sky/30 bg-sky/10 p-4">
        <Activity className="mt-0.5 size-5 text-sky" />
        <p className="text-sm leading-6 text-white/[0.74]">
          AgroSense compares soil, weather, crop image, and farmer questions
          against dedicated AI workflows.
        </p>
      </div>
    </motion.div>
  );
}
