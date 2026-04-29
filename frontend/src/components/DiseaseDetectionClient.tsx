"use client";
/* eslint-disable @next/next/no-img-element */

import { DragEvent, FormEvent, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Camera, ImagePlus, Loader2, Microscope, UploadCloud, X } from "lucide-react";

type DiseaseResult = {
  status: string;
  detection: {
    plant: string;
    disease: string;
    confidence: number;
    predicted_class: string;
    top3: Array<{ class: string; confidence: number }>;
  };
  summary?: {
    disease_name?: string;
    description?: string;
    causes?: string;
    symptoms?: string;
    immediate_action?: string;
    cure?: string;
    prevention?: string;
    organic_solution?: string;
    severity?: string;
    error?: string;
    raw_text?: string;
  };
};

export function DiseaseDetectionClient() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [query, setQuery] = useState("What treatment should I use?");
  const [lang, setLang] = useState("en");
  const [result, setResult] = useState<DiseaseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraLoading, setCameraLoading] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  useEffect(() => {
    if (!cameraOpen || !videoRef.current || !streamRef.current) return;
    videoRef.current.srcObject = streamRef.current;
    void videoRef.current.play();
  }, [cameraOpen]);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  function selectFile(selected: File | undefined) {
    if (!selected) return;
    if (preview) URL.revokeObjectURL(preview);
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
    setError("");
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraOpen(false);
    setCameraLoading(false);
  }

  async function startCamera() {
    setCameraError("");
    setError("");

    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError("Camera capture is not supported in this browser.");
      return;
    }

    try {
      stopCamera();
      setCameraLoading(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false,
      });
      streamRef.current = stream;
      setCameraOpen(true);
    } catch (exc) {
      const denied =
        exc instanceof DOMException &&
        ["NotAllowedError", "PermissionDeniedError"].includes(exc.name);
      setCameraError(
        denied
          ? "Camera permission was denied. Allow camera access or upload an image instead."
          : "Camera could not start. Please try again or upload an image.",
      );
    } finally {
      setCameraLoading(false);
    }
  }

  function captureCameraImage() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) {
      setCameraError("Camera preview is not ready yet.");
      return;
    }

    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d");
    if (!context) {
      setCameraError("Unable to capture from camera.");
      return;
    }

    context.drawImage(video, 0, 0, width, height);
    canvas.toBlob((blob) => {
      if (!blob) {
        setCameraError("Unable to save captured image.");
        return;
      }
      const capturedFile = new File([blob], `agrosense-camera-${Date.now()}.jpg`, {
        type: "image/jpeg",
      });
      selectFile(capturedFile);
      stopCamera();
    }, "image/jpeg", 0.92);
  }

  function onDrop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    selectFile(event.dataTransfer.files[0]);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Upload a leaf or crop image first.");
      return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("image", file);
    formData.append("query", query);
    formData.append("lang", lang);

    try {
      const response = await fetch("/api/disease", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || data.error || data.message || "Disease detection failed.");
      setResult(data as DiseaseResult);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Disease detection failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[0.9fr_1fr]">
      <form onSubmit={submit} className="rounded-2xl border border-line bg-white/[0.78] p-6">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-earth">
              Leaf image diagnosis
            </p>
            <h2 className="mt-2 font-serif text-3xl font-semibold text-primary">
              Upload crop image
            </h2>
          </div>
          <span className="grid size-12 place-items-center rounded-xl bg-mint text-primary">
            <Microscope className="size-5" />
          </span>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp,image/bmp"
          capture="environment"
          className="hidden"
          onChange={(event) => selectFile(event.target.files?.[0])}
        />
        <canvas ref={canvasRef} className="hidden" />

        <div className="mb-4 grid gap-3 sm:grid-cols-2">
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-line bg-cream px-4 py-3 text-sm font-bold text-primary transition hover:border-sage"
          >
            <ImagePlus className="size-4" />
            Upload Image
          </button>
          <button
            type="button"
            onClick={() => void startCamera()}
            disabled={cameraLoading}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-line bg-cream px-4 py-3 text-sm font-bold text-primary transition hover:border-sage disabled:opacity-60"
          >
            {cameraLoading ? <Loader2 className="size-4 animate-spin" /> : <Camera className="size-4" />}
            Use Camera
          </button>
        </div>

        {cameraError ? (
          <p className="mb-4 rounded-xl border border-danger/20 bg-danger/10 px-4 py-3 text-sm font-semibold text-danger">
            {cameraError}
          </p>
        ) : null}

        {cameraOpen ? (
          <div className="mb-4 rounded-2xl border border-sage/40 bg-cream p-4">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="h-72 w-full rounded-xl bg-primary object-cover"
            />
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={captureCameraImage}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-bold text-white transition hover:bg-primary-soft"
              >
                <Camera className="size-4" />
                Capture
              </button>
              <button
                type="button"
                onClick={stopCamera}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-line bg-white px-4 py-3 text-sm font-bold text-primary transition hover:border-sage"
              >
                <X className="size-4" />
                Close camera
              </button>
            </div>
          </div>
        ) : null}

        <button
          type="button"
          onDrop={onDrop}
          onDragOver={(event) => event.preventDefault()}
          className="w-full cursor-pointer rounded-2xl border-2 border-dashed border-sage/60 bg-cream p-6 text-center transition hover:border-primary"
          onClick={() => inputRef.current?.click()}
        >
          {preview ? (
            <img
              src={preview}
              alt="Uploaded crop preview"
              className="mx-auto h-72 w-full rounded-xl object-cover"
            />
          ) : (
            <div className="grid min-h-72 place-items-center">
              <div>
                <UploadCloud className="mx-auto mb-4 size-12 text-primary" />
                <p className="font-serif text-2xl font-semibold text-primary">
                  Drag and drop a leaf image
                </p>
                <p className="mt-2 text-sm text-muted">
                  JPG, PNG, WEBP, or BMP images are supported.
                </p>
              </div>
            </div>
          )}
        </button>

        <label className="mt-5 block">
          <span className="mb-2 block text-sm font-bold text-primary">
            Advisory question
          </span>
          <textarea
            className="field-control min-h-28 resize-none"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>

        <label className="mt-5 block">
          <span className="mb-2 block text-sm font-bold text-primary">
            Advice language
          </span>
          <select
            className="field-control"
            value={lang}
            onChange={(event) => setLang(event.target.value)}
          >
            <option value="en">English</option>
            <option value="hi-IN">Hindi</option>
            <option value="pa-IN">Punjabi</option>
          </select>
        </label>

        {error ? <p className="mt-4 text-sm font-semibold text-danger">{error}</p> : null}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 py-4 text-sm font-bold text-white transition hover:bg-primary-soft disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? <Loader2 className="size-4 animate-spin" /> : <ImagePlus className="size-4" />}
          Analyze image
        </button>
      </form>

      <div className="rounded-2xl bg-primary p-6 text-white">
        {result ? (
          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
            <p className="text-xs font-bold uppercase tracking-widest text-gold">
              Disease result
            </p>
            <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-sm text-white/[0.58]">{result.detection.plant}</p>
                <h3 className="font-serif text-5xl font-semibold">
                  {result.detection.disease}
                </h3>
              </div>
              <div className="rounded-xl bg-white/10 px-5 py-3 text-right">
                <p className="text-xs text-white/[0.58]">Confidence</p>
                <p className="font-serif text-3xl font-semibold text-gold">
                  {result.detection.confidence.toFixed(1)}%
                </p>
              </div>
            </div>

            <div className="mt-6 rounded-xl border border-sky/30 bg-sky/10 p-4">
              <p className="text-xs font-bold uppercase tracking-widest text-sky">
                Gemini disease summary
              </p>
              {result.summary?.error ? (
                <p className="mt-3 whitespace-pre-line text-sm leading-6 text-white/[0.80]">
                  {result.summary.error}: {result.summary.raw_text}
                </p>
              ) : (
                <div className="mt-3 space-y-3 text-sm leading-6 text-white/[0.80]">
                  <p>{result.summary?.description}</p>
                  <p><span className="font-bold text-white">Immediate action:</span> {result.summary?.immediate_action}</p>
                  <p><span className="font-bold text-white">Cure:</span> {result.summary?.cure}</p>
                  <p><span className="font-bold text-white">Prevention:</span> {result.summary?.prevention}</p>
                  <p><span className="font-bold text-white">Organic solution:</span> {result.summary?.organic_solution}</p>
                  <p><span className="font-bold text-white">Severity:</span> {result.summary?.severity}</p>
                </div>
              )}
            </div>

            <div className="mt-4 rounded-xl border border-white/10 bg-white/10 p-4 text-xs text-white/[0.62]">
              <p>Model: PlantDiseaseDetectorVit2</p>
              <p>Raw class: {result.detection.predicted_class}</p>
              <p>
                Top 3: {result.detection.top3.map((item) => `${item.class} (${item.confidence}%)`).join(", ")}
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="flex min-h-[520px] flex-col justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-gold">
                Result preview
              </p>
              <h3 className="mt-3 font-serif text-4xl font-semibold">
                Disease, confidence, and Gemini advice appear here.
              </h3>
              <p className="mt-5 max-w-md leading-7 text-mint">
                The backend sends your image to the plant disease model and
                passes the result to the advisory assistant.
              </p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/10 p-4 text-sm text-white/[0.66]">
              Backend route: POST /disease/analyze
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
