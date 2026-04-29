import { Mail, MapPin, MessageCircle, Share2 } from "lucide-react";
import { ContactForm } from "@/components/ContactForm";
import { PageHero } from "@/components/PageHero";

export default function ContactPage() {
  return (
    <>
      <PageHero
        eyebrow="Contact"
        title="Bring AgroSense to your farm, team, or demo."
        description="Use the contact form or reach out directly for product questions, model integration, or deployment planning."
        image="https://images.unsplash.com/photo-1472145246862-b24cf25c4a36?auto=format&fit=crop&w=1800&q=80"
      />
      <section className="page-band bg-primary text-white">
        <div className="container-frame grid gap-10 lg:grid-cols-[0.8fr_1fr] lg:items-start">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-gold">
              Get in touch
            </p>
            <h2 className="mt-3 font-serif text-4xl font-semibold">
              We would love to hear what you are growing.
            </h2>
            <div className="mt-8 grid gap-4">
              <a href="mailto:hello@agrosense.ai" className="flex items-center gap-3 text-mint">
                <Mail className="size-5 text-gold" />
                hello@agrosense.ai
              </a>
              <p className="flex items-center gap-3 text-mint">
                <MapPin className="size-5 text-gold" />
                Built for farmers and agri teams everywhere
              </p>
              <div className="flex gap-3 pt-2">
                <a
                  aria-label="LinkedIn"
                  href="#"
                  className="grid size-11 place-items-center rounded-xl border border-white/10 bg-white/10 text-gold"
                >
                  <Share2 className="size-5" />
                </a>
                <a
                  aria-label="Twitter"
                  href="#"
                  className="grid size-11 place-items-center rounded-xl border border-white/10 bg-white/10 text-gold"
                >
                  <MessageCircle className="size-5" />
                </a>
              </div>
            </div>
          </div>
          <ContactForm />
        </div>
      </section>
    </>
  );
}
