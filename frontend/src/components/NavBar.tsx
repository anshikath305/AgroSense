"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, Sprout, X } from "lucide-react";
import { useState } from "react";
import { navItems } from "@/lib/content";

export function NavBar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-white/30 bg-cream/[0.82] backdrop-blur-2xl">
      <div className="container-frame flex h-20 items-center justify-between gap-5">
        <Link href="/" className="flex items-center gap-3 text-primary">
          <span className="grid size-11 place-items-center rounded-xl bg-primary text-gold">
            <Sprout className="size-5" />
          </span>
          <span>
            <span className="block font-serif text-2xl font-semibold leading-none">
              AgroSense
            </span>
            <span className="block text-xs font-semibold uppercase tracking-widest text-muted">
              Smart Farming AI
            </span>
          </span>
        </Link>

        <nav className="hidden items-center gap-5 lg:flex">
          {navItems.map((item) => {
            const active = item.href !== "/#features" && pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`text-sm font-semibold transition ${
                  active ? "text-primary" : "text-muted hover:text-primary"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <Link
            href="/login"
            className="rounded-xl px-4 py-2 text-sm font-semibold text-primary transition hover:bg-white/60"
          >
            Login
          </Link>
          <Link
            href="/crop-ai"
            className="rounded-xl bg-gold px-5 py-3 text-sm font-bold text-primary transition hover:brightness-105"
          >
            Try Now
          </Link>
        </div>

        <button
          type="button"
          aria-label="Toggle navigation"
          className="grid size-11 place-items-center rounded-xl border border-line bg-white/70 text-primary lg:hidden"
          onClick={() => setOpen((value) => !value)}
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      {open ? (
        <div className="border-t border-line bg-cream/[0.96] px-4 py-5 lg:hidden">
          <nav className="container-frame grid gap-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-xl px-4 py-3 text-sm font-semibold text-primary hover:bg-white/70"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <Link
              href="/crop-ai"
              className="mt-2 rounded-xl bg-gold px-4 py-3 text-center text-sm font-bold text-primary"
              onClick={() => setOpen(false)}
            >
              Try Now
            </Link>
          </nav>
        </div>
      ) : null}
    </header>
  );
}
