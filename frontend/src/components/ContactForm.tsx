"use client";

import { FormEvent, useState } from "react";
import { Send } from "lucide-react";

export function ContactForm() {
  const [submitted, setSubmitted] = useState(false);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
  }

  return (
    <form onSubmit={submit} className="rounded-2xl border border-white/10 bg-white/10 p-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-2 block text-sm font-bold text-white">Name</span>
          <input className="field-control" placeholder="Your name" required />
        </label>
        <label>
          <span className="mb-2 block text-sm font-bold text-white">Email</span>
          <input className="field-control" type="email" placeholder="you@example.com" required />
        </label>
      </div>
      <label className="mt-4 block">
        <span className="mb-2 block text-sm font-bold text-white">Message</span>
        <textarea
          className="field-control min-h-32 resize-none"
          placeholder="Tell us about your farm or MVP needs"
          required
        />
      </label>
      {submitted ? (
        <p className="mt-4 rounded-xl bg-gold/20 px-4 py-3 text-sm font-semibold text-gold">
          Message captured for the MVP demo.
        </p>
      ) : null}
      <button
        type="submit"
        className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gold px-6 py-4 text-sm font-bold text-primary"
      >
        Send message
        <Send className="size-4" />
      </button>
    </form>
  );
}
