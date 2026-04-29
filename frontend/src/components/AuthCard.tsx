"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ArrowRight, Sprout } from "lucide-react";

type AuthCardProps = {
  mode: "login" | "signup";
};

export function AuthCard({ mode }: AuthCardProps) {
  const [submitted, setSubmitted] = useState(false);
  const isLogin = mode === "login";

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
  }

  return (
    <div className="mx-auto grid min-h-[calc(100svh-80px)] max-w-6xl gap-8 px-4 py-12 lg:grid-cols-[0.9fr_1fr] lg:items-center">
      <section className="rounded-3xl bg-primary p-8 text-white">
        <span className="grid size-12 place-items-center rounded-xl bg-gold text-primary">
          <Sprout className="size-5" />
        </span>
        <h1 className="mt-8 font-serif text-5xl font-semibold">
          AgroSense account access
        </h1>
        <p className="mt-5 text-lg leading-8 text-mint">
          Auth screens are prepared for a future dashboard while the MVP stays
          focused on public AI farming tools.
        </p>
      </section>
      <form onSubmit={submit} className="rounded-2xl border border-line bg-white/[0.82] p-6">
        <p className="text-xs font-bold uppercase tracking-widest text-earth">
          {isLogin ? "Welcome back" : "Create account"}
        </p>
        <h2 className="mt-2 font-serif text-4xl font-semibold text-primary">
          {isLogin ? "Login" : "Sign up"}
        </h2>
        <div className="mt-8 grid gap-4">
          {!isLogin ? (
            <label>
              <span className="mb-2 block text-sm font-bold text-primary">Name</span>
              <input className="field-control" placeholder="Your name" required />
            </label>
          ) : null}
          <label>
            <span className="mb-2 block text-sm font-bold text-primary">Email</span>
            <input className="field-control" type="email" placeholder="farmer@example.com" required />
          </label>
          <label>
            <span className="mb-2 block text-sm font-bold text-primary">Password</span>
            <input className="field-control" type="password" placeholder="Password" required />
          </label>
        </div>
        {submitted ? (
          <p className="mt-4 rounded-xl bg-mint px-4 py-3 text-sm font-semibold text-primary">
            Auth structure is ready. Connect a provider when the dashboard phase begins.
          </p>
        ) : null}
        <button
          type="submit"
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 py-4 text-sm font-bold text-white"
        >
          {isLogin ? "Login" : "Create account"}
          <ArrowRight className="size-4" />
        </button>
        <p className="mt-5 text-center text-sm text-muted">
          {isLogin ? "New to AgroSense?" : "Already have an account?"}{" "}
          <Link href={isLogin ? "/signup" : "/login"} className="font-bold text-primary">
            {isLogin ? "Sign up" : "Login"}
          </Link>
        </p>
      </form>
    </div>
  );
}
