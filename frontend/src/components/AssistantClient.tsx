"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Bot, ImagePlus, Loader2, Mic, Pause, Play, Send, Square, UserRound } from "lucide-react";
import { assistantPrompts } from "@/lib/content";

type Message = {
  role: "assistant" | "user";
  content: string;
};

type SpeechState = "idle" | "speaking" | "paused";

type SpeechRecognitionEventLike = Event & {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
};

type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

type SpeechWindow = Window & {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
};

export function AssistantClient() {
  const initialAssistantMessage =
    "Ask me about crop symptoms, fertilizer planning, pest control, irrigation timing, or field recovery after weather stress.";
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: initialAssistantMessage,
    },
  ]);
  const [input, setInput] = useState("");
  const [lang, setLang] = useState("en");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [speechState, setSpeechState] = useState<SpeechState>("idle");
  const [lastSpokenText, setLastSpokenText] = useState(initialAssistantMessage);
  const [speechNotice, setSpeechNotice] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const speechLang = lang === "hi-IN" ? "hi-IN" : lang === "pa-IN" ? "pa-IN" : lang === "ta-IN" ? "ta-IN" : "en-US";

  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  function speechEngine() {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setSpeechNotice("Speech playback is not supported in this browser.");
      setSpeechState("idle");
      return null;
    }
    return window.speechSynthesis;
  }

  function startSpeech(text?: string) {
    const speech = speechEngine();
    const content = (text ?? lastSpokenText).trim();
    if (!speech || !content) return;

    utteranceRef.current = null;
    speech.cancel();
    const utterance = new SpeechSynthesisUtterance(content);
    utterance.lang = speechLang;
    utterance.onstart = () => setSpeechState("speaking");
    utterance.onpause = () => setSpeechState("paused");
    utterance.onresume = () => setSpeechState("speaking");
    utterance.onend = () => {
      if (utteranceRef.current === utterance) {
        utteranceRef.current = null;
        setSpeechState("idle");
      }
    };
    utterance.onerror = () => {
      utteranceRef.current = null;
      setSpeechState("idle");
      setSpeechNotice("Speech playback stopped unexpectedly. You can try Speak again.");
    };

    utteranceRef.current = utterance;
    setLastSpokenText(content);
    setSpeechNotice("");
    setSpeechState("speaking");
    speech.speak(utterance);
  }

  function pauseSpeech() {
    const speech = speechEngine();
    if (!speech || speechState !== "speaking") return;
    speech.pause();
    setSpeechState("paused");
  }

  function resumeSpeech() {
    const speech = speechEngine();
    if (!speech || speechState !== "paused") return;
    speech.resume();
    setSpeechState("speaking");
  }

  function stopSpeech() {
    const speech = speechEngine();
    if (!speech) return;
    speech.cancel();
    utteranceRef.current = null;
    setSpeechState("idle");
  }

  function startVoiceInput() {
    if (typeof window === "undefined") return;
    const speechWindow = window as SpeechWindow;
    const SpeechRecognition =
      speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: "Voice input is not supported in this browser. Please type your question.",
        },
      ]);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = speechLang;
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript ?? "";
      setInput((current) => `${current} ${transcript}`.trim());
    };
    recognition.onerror = () => {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: "I could not hear that clearly. Please try voice input again or type the question.",
        },
      ]);
    };
    recognition.onend = () => setListening(false);
    setListening(true);
    recognition.start();
  }

  async function ask(event?: FormEvent<HTMLFormElement>, prompt?: string) {
    event?.preventDefault();
    const query = (prompt ?? input).trim();
    if (!query || loading) return;

    setMessages((current) => [...current, { role: "user", content: query }]);
    setInput("");
    setLoading(true);

    try {
      const requestInit: RequestInit = imageFile
        ? {
            method: "POST",
            body: (() => {
              const formData = new FormData();
              formData.append("query", query);
              formData.append("lang", lang);
              formData.append("image", imageFile);
              return formData;
            })(),
          }
        : {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, lang }),
          };
      const response = await fetch("/api/advisory", requestInit);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || data.error || "Advisory request failed.");
      const advice = String(data.advice || "").trim();
      if (!advice) throw new Error("Gemini returned an empty advisory response.");
      setMessages((current) => [
        ...current,
        { role: "assistant", content: advice },
      ]);
      startSpeech(advice);
      setImageFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "I could not reach the advisory service. Check the backend, then try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[0.74fr_1fr]">
      <aside className="rounded-2xl border border-line bg-white/[0.78] p-6">
        <p className="text-xs font-bold uppercase tracking-widest text-earth">
          Farming copilot
        </p>
        <h2 className="mt-2 font-serif text-3xl font-semibold text-primary">
          Ask AgroSense AI
        </h2>
        <p className="mt-4 text-sm leading-6 text-muted">
          Responses are concise, practical, multilingual, and powered by the live
          advisory endpoint for text, voice, and crop image questions.
        </p>

        <label className="mt-6 block">
          <span className="mb-2 block text-sm font-bold text-primary">
            Response language
          </span>
          <select
            className="field-control"
            value={lang}
            onChange={(event) => setLang(event.target.value)}
          >
            <option value="en">English</option>
            <option value="hi-IN">Hindi</option>
            <option value="pa-IN">Punjabi</option>
            <option value="ta-IN">Tamil</option>
          </select>
        </label>

        <div className="mt-8">
          <p className="mb-3 text-sm font-bold text-primary">Suggested prompts</p>
          <div className="grid gap-2">
            {assistantPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => void ask(undefined, prompt)}
                className="rounded-xl border border-line bg-cream px-4 py-3 text-left text-sm font-semibold text-primary transition hover:border-sage"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </aside>

      <section className="overflow-hidden rounded-2xl bg-primary text-white">
        <div className="border-b border-white/10 p-5">
          <div className="flex items-center gap-3">
            <span className="grid size-11 place-items-center rounded-xl bg-gold text-primary">
              <Bot className="size-5" />
            </span>
            <div>
              <h2 className="font-serif text-2xl font-semibold">
                Advisory Assistant
              </h2>
              <p className="text-sm text-mint">Card based answers for field decisions</p>
            </div>
          </div>
        </div>

        <div className="max-h-[620px] min-h-[520px] space-y-5 overflow-y-auto p-5">
          {messages.map((message, index) => (
            <motion.div
              key={`${message.role}-${index}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${message.role === "user" ? "justify-end" : ""}`}
            >
              {message.role === "assistant" ? (
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-gold text-primary">
                  <Bot className="size-5" />
                </span>
              ) : null}
              <div
                className={
                  message.role === "assistant"
                    ? "max-w-2xl whitespace-pre-line rounded-2xl border border-white/10 bg-white/10 p-4 text-sm leading-6 text-mint"
                    : "max-w-2xl rounded-2xl bg-gold p-4 text-sm font-semibold leading-6 text-primary"
                }
              >
                {message.content}
              </div>
              {message.role === "user" ? (
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-white/10 text-white">
                  <UserRound className="size-5" />
                </span>
              ) : null}
            </motion.div>
          ))}
          {loading ? (
            <div className="flex items-center gap-2 text-sm text-mint">
              <Loader2 className="size-4 animate-spin" />
              AgroSense is thinking
            </div>
          ) : null}
        </div>

        <div className="border-t border-white/10 px-4 py-3">
          <div className="flex flex-wrap items-center gap-2">
            {speechState === "idle" ? (
              <button
                type="button"
                onClick={() => startSpeech()}
                disabled={!lastSpokenText}
                className="inline-flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2 text-xs font-bold text-mint transition hover:bg-white/15 disabled:opacity-50"
              >
                <Play className="size-4" />
                Speak
              </button>
            ) : null}
            {speechState === "speaking" ? (
              <button
                type="button"
                onClick={pauseSpeech}
                className="inline-flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2 text-xs font-bold text-mint transition hover:bg-white/15"
              >
                <Pause className="size-4" />
                Pause
              </button>
            ) : null}
            {speechState === "paused" ? (
              <button
                type="button"
                onClick={resumeSpeech}
                className="inline-flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2 text-xs font-bold text-mint transition hover:bg-white/15"
              >
                <Play className="size-4" />
                Resume
              </button>
            ) : null}
            {speechState !== "idle" ? (
              <button
                type="button"
                onClick={stopSpeech}
                className="inline-flex items-center gap-2 rounded-xl bg-gold px-3 py-2 text-xs font-bold text-primary transition hover:brightness-105"
              >
                <Square className="size-4" />
                Stop
              </button>
            ) : null}
            <span className="text-xs text-white/[0.48]">
              {speechState === "idle" ? "Ready to speak latest answer" : speechState === "paused" ? "Paused" : "Speaking"}
            </span>
          </div>
          {speechNotice ? <p className="mt-2 text-xs text-gold">{speechNotice}</p> : null}
        </div>

        <form onSubmit={ask} className="border-t border-white/10 p-4">
          <div className="flex items-end gap-2 rounded-2xl border border-white/10 bg-white/10 p-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/bmp"
              className="hidden"
              onChange={(event) => setImageFile(event.target.files?.[0] ?? null)}
            />
            <button
              type="button"
              aria-label="Upload image"
              onClick={() => fileInputRef.current?.click()}
              className={`grid size-11 place-items-center rounded-xl text-mint transition hover:bg-white/10 ${
                imageFile ? "bg-white/10 text-gold" : ""
              }`}
            >
              <ImagePlus className="size-5" />
            </button>
            <button
              type="button"
              aria-label="Voice input"
              onClick={startVoiceInput}
              className={`grid size-11 place-items-center rounded-xl text-mint transition hover:bg-white/10 ${
                listening ? "bg-white/10 text-gold" : ""
              }`}
            >
              <Mic className="size-5" />
            </button>
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              rows={1}
              placeholder="Ask about your crop, soil, fertilizer, or pest issue..."
              className="min-h-11 flex-1 resize-none border-0 bg-transparent px-2 py-3 text-sm text-white outline-none placeholder:text-white/[0.42]"
            />
            <button
              type="submit"
              disabled={loading}
              aria-label="Send message"
              className="grid size-11 place-items-center rounded-xl bg-gold text-primary transition hover:brightness-105 disabled:opacity-60"
            >
              <Send className="size-5" />
            </button>
          </div>
          {imageFile ? (
            <p className="mt-2 text-xs text-mint">
              Image attached: {imageFile.name}
            </p>
          ) : null}
        </form>
      </section>
    </div>
  );
}
