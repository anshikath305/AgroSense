"use client";

import { FormEvent, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Sparkles, Sprout } from "lucide-react";
import { cropExamples } from "@/lib/content";

type CropResult = {
  recommended_crop: string;
  confidence: number;
  why_recommended: string;
  best_season: string;
  expected_benefits: string;
  alternatives: { crop: string; confidence: number }[];
};

const fieldConfig = [
  { key: "N", label: "Nitrogen", unit: "kg/ha" },
  { key: "P", label: "Phosphorus", unit: "kg/ha" },
  { key: "K", label: "Potassium", unit: "kg/ha" },
  { key: "temperature", label: "Temperature", unit: "C" },
  { key: "humidity", label: "Humidity", unit: "%" },
  { key: "ph", label: "pH", unit: "0-14" },
  { key: "rainfall", label: "Rainfall", unit: "mm" },
] as const;

type FieldKey = (typeof fieldConfig)[number]["key"];

const initialValues: Record<FieldKey, string> = {
  N: "90",
  P: "42",
  K: "43",
  temperature: "22",
  humidity: "82",
  ph: "6.5",
  rainfall: "202",
};

export function CropRecommendationClient() {
  const [values, setValues] = useState(initialValues);
  const [result, setResult] = useState<CropResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const payload = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(values).map(([key, value]) => [key, Number(value)]),
      ),
    [values],
  );

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/crop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || data.error || "Crop recommendation failed.");
      setResult(data as CropResult);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Crop recommendation failed.");
    } finally {
      setLoading(false);
    }
  }

  function loadExample(valuesToLoad: number[]) {
    setValues(
      Object.fromEntries(
        fieldConfig.map((field, index) => [field.key, String(valuesToLoad[index])]),
      ) as Record<FieldKey, string>,
    );
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[0.92fr_1fr]">
      <form onSubmit={submit} className="rounded-2xl border border-line bg-white/[0.78] p-6">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-earth">
              Soil and climate
            </p>
            <h2 className="mt-2 font-serif text-3xl font-semibold text-primary">
              Enter field values
            </h2>
          </div>
          <span className="grid size-12 place-items-center rounded-xl bg-mint text-primary">
            <Sprout className="size-5" />
          </span>
        </div>

        <div className="mb-6 flex flex-wrap gap-2">
          {cropExamples.map((example) => (
            <button
              key={example.label}
              type="button"
              onClick={() => loadExample(example.values)}
              className="rounded-full border border-line bg-cream px-3 py-2 text-xs font-bold text-primary transition hover:border-sage"
            >
              {example.label}
            </button>
          ))}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {fieldConfig.map((field) => (
            <label key={field.key} className="block">
              <span className="mb-2 flex justify-between text-sm font-bold text-primary">
                {field.label}
                <span className="font-medium text-muted">{field.unit}</span>
              </span>
              <input
                className="field-control"
                type="number"
                step="any"
                min={field.key === "ph" ? 0 : undefined}
                max={field.key === "ph" ? 14 : field.key === "humidity" ? 100 : undefined}
                value={values[field.key]}
                onChange={(event) =>
                  setValues((current) => ({
                    ...current,
                    [field.key]: event.target.value,
                  }))
                }
              />
            </label>
          ))}
        </div>

        {error ? <p className="mt-4 text-sm font-semibold text-danger">{error}</p> : null}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 py-4 text-sm font-bold text-white transition hover:bg-primary-soft disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
          Recommend crop
        </button>
      </form>

      <div className="rounded-2xl bg-primary p-6 text-white">
        {result ? (
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid h-full content-between gap-6"
          >
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-gold">
                Recommended crop
              </p>
              <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
                <h3 className="font-serif text-5xl font-semibold">
                  {result.recommended_crop}
                </h3>
                <div className="rounded-xl bg-white/10 px-5 py-3 text-right">
                  <p className="text-xs text-white/[0.58]">Confidence</p>
                  <p className="font-serif text-3xl font-semibold text-gold">
                    {result.confidence}%
                  </p>
                </div>
              </div>
              <p className="mt-6 text-base leading-7 text-mint">
                {result.why_recommended}
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-bold uppercase tracking-widest text-gold">
                  Best season
                </p>
                <p className="mt-2 font-semibold">{result.best_season}</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-bold uppercase tracking-widest text-gold">
                  Expected benefits
                </p>
                <p className="mt-2 text-sm leading-6 text-white/[0.78]">
                  {result.expected_benefits}
                </p>
              </div>
            </div>

            <div>
              <p className="mb-3 text-xs font-bold uppercase tracking-widest text-white/50">
                Top alternatives
              </p>
              <div className="grid gap-3">
                {result.alternatives.map((item) => (
                  <div
                    key={item.crop}
                    className="flex items-center justify-between rounded-xl bg-white/[0.08] p-3"
                  >
                    <span className="font-semibold">{item.crop}</span>
                    <span className="text-gold">{item.confidence}%</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        ) : (
          <div className="flex min-h-[520px] flex-col justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-gold">
                Result preview
              </p>
              <h3 className="mt-3 font-serif text-4xl font-semibold">
                A model-backed result appears here.
              </h3>
              <p className="mt-5 max-w-md leading-7 text-mint">
                Submit field data to see recommended crop, confidence, season,
                benefits, and model-ranked alternatives.
              </p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/10 p-4 text-sm text-white/[0.66]">
              Backend route: POST /crop/predict
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
