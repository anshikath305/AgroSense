import Link from "next/link";
import { Mail, Sprout } from "lucide-react";
import { navItems } from "@/lib/content";

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-primary text-white">
      <div className="container-frame grid gap-10 py-12 lg:grid-cols-[1.2fr_1fr_1fr]">
        <div>
          <div className="mb-4 flex items-center gap-3">
            <span className="grid size-11 place-items-center rounded-xl bg-gold text-primary">
              <Sprout className="size-5" />
            </span>
            <span className="font-serif text-2xl font-semibold">AgroSense</span>
          </div>
          <p className="max-w-md text-sm leading-6 text-mint">
            Premium AI tools for better crop choice, faster disease response,
            smarter nutrient planning, and practical farming advice.
          </p>
        </div>
        <div>
          <h3 className="mb-4 text-sm font-bold uppercase tracking-widest text-gold">
            Platform
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {navItems.slice(0, 8).map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-sm text-white/[0.72] transition hover:text-white"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
        <div>
          <h3 className="mb-4 text-sm font-bold uppercase tracking-widest text-gold">
            Contact
          </h3>
          <a
            href="mailto:hello@agrosense.ai"
            className="mb-4 flex items-center gap-2 text-sm text-white/[0.78] hover:text-white"
          >
            <Mail className="size-4" />
            hello@agrosense.ai
          </a>
          <p className="text-sm text-white/[0.58]">
            Built for MVP v1. IoT features are intentionally out of scope.
          </p>
        </div>
      </div>
      <div className="border-t border-white/10 py-5">
        <div className="container-frame flex flex-col gap-2 text-xs text-white/[0.54] sm:flex-row sm:items-center sm:justify-between">
          <span>AgroSense MVP v1</span>
          <span>AI powered smart farming platform</span>
        </div>
      </div>
    </footer>
  );
}
