"use client";

import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { FlaskConical, Loader2, Sparkles } from "lucide-react";
import { cropTypes, soilTypes } from "@/lib/content";

type FertilizerResult = {
  recommended_fertilizer: string;
  recommended_quantity_kg_per_acre: number;
  usage_instructions: string;
  why_recommended: string;
  nutrient_balance: {
    nitrogen: number;
    phosphorous: number;
    potassium: number;
    moisture: number;
  };
};

const initialValues = {
  temperature: "29",
  humidity: "52",
  moisture: "45",
  soil_type: "Loamy",
  crop_type: "Sugarcane",
  nitrogen: "12",
  potassium: "0",
  phosphorous: "36",
};

export function FertilizerPredictionClient() {
  const [values, setValues] = useState(initialValues);
  const [result, setResult] = useState<FertilizerResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    const payload = {
      temperature: Number(values.temperature),
      humidity: Number(values.humidity),
      moisture: Number(values.moisture),
      soil_type: values.soil_type,
      crop_type: values.crop_type,
      nitrogen: Number(values.nitrogen),
      potassium: Number(values.potassium),
      phosphorous: Number(values.phosphorous),
    };

    try {
      const response = await fetch("/api/fertilizer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || data.error || "Fertilizer prediction failed.");
      setResult(data as FertilizerResult);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Fertilizer prediction failed.");
    } finally {
      setLoading(false);
    }
  }

  function setValue(key: keyof typeof initialValues, value: string) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[0.9fr_1fr]">
      <form onSubmit={submit} className="rounded-2xl border border-line bg-white/[0.78] p-6">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-earth">
              Smart nutrient planning
            </p>
            <h2 className="mt-2 font-serif text-3xl font-semibold text-primary">
              Field and soil inputs
            </h2>
          </div>
          <span className="grid size-12 place-items-center rounded-xl bg-mint text-primary">
            <FlaskConical className="size-5" />
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <label>
            <span className="mb-2 block text-sm font-bold text-primary">Soil type</span>
            <select
              className="field-control"
              value={values.soil_type}
              onChange={(event) => setValue("soil_type", event.target.value)}
            >
              {soilTypes.map((soil) => (
                <option key={soil}>{soil}</option>
              ))}
            </select>
          </label>
          <label>
            <span className="mb-2 block text-sm font-bold text-primary">Crop type</span>
            <select
              className="field-control"
              value={values.crop_type}
              onChange={(event) => setValue("crop_type", event.target.value)}
            >
              {cropTypes.map((crop) => (
                <option key={crop}>{crop}</option>
              ))}
            </select>
          </label>
          {[
            ["temperature", "Temperature", "C"],
            ["humidity", "Humidity", "%"],
            ["moisture", "Moisture", "%"],
            ["nitrogen", "Nitrogen", "kg/ha"],
            ["potassium", "Potassium", "kg/ha"],
            ["phosphorous", "Phosphorus", "kg/ha"],
          ].map(([key, label, unit]) => (
            <label key={key}>
              <span className="mb-2 flex justify-between text-sm font-bold text-primary">
                {label}
                <span className="font-medium text-muted">{unit}</span>
              </span>
              <input
                type="number"
                step="any"
                className="field-control"
                value={values[key as keyof typeof initialValues]}
                onChange={(event) =>
                  setValue(key as keyof typeof initialValues, event.target.value)
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
          Predict fertilizer
        </button>
      </form>

      <div className="rounded-2xl bg-primary p-6 text-white">
        {result ? (
          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
            <p className="text-xs font-bold uppercase tracking-widest text-gold">
              Recommended fertilizer
            </p>
            <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
              <h3 className="font-serif text-5xl font-semibold">
                {result.recommended_fertilizer}
              </h3>
              <div className="rounded-xl bg-white/10 px-5 py-3 text-right">
                <p className="text-xs text-white/[0.58]">Quantity</p>
                <p className="font-serif text-3xl font-semibold text-gold">
                  {result.recommended_quantity_kg_per_acre} kg/acre
                </p>
              </div>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-bold uppercase tracking-widest text-gold">
                  Why recommended
                </p>
                <p className="mt-3 text-sm leading-6 text-mint">
                  {result.why_recommended}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-bold uppercase tracking-widest text-gold">
                  Usage instructions
                </p>
                <p className="mt-3 text-sm leading-6 text-mint">
                  {result.usage_instructions}
                </p>
              </div>
            </div>
            <div className="mt-6">
              <p className="mb-3 text-xs font-bold uppercase tracking-widest text-white/50">
                Nutrient snapshot
              </p>
              <div className="grid gap-3 sm:grid-cols-4">
                {Object.entries(result.nutrient_balance).map(([key, value]) => (
                  <div key={key} className="rounded-xl bg-white/[0.08] p-4">
                    <p className="text-xs capitalize text-white/[0.58]">{key}</p>
                    <p className="mt-1 font-serif text-2xl font-semibold">{value}</p>
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
                Fertilizer type and quantity appear here.
              </h3>
              <p className="mt-5 max-w-md leading-7 text-mint">
                Submit soil, crop, moisture, and nutrient data to run the
                fertilizer classifier and quantity regressor.
              </p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/10 p-4 text-sm text-white/[0.66]">
              Backend route: POST /fertilizer/predict
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
