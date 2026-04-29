import { AssistantClient } from "@/components/AssistantClient";
import { PageHero } from "@/components/PageHero";

export default function AssistantPage() {
  return (
    <>
      <PageHero
        eyebrow="AI Farming Advisory Assistant"
        title="Ask practical farming questions in a clean chat workspace."
        description="A ChatGPT-style agricultural assistant for crop symptoms, fertilizer choices, pest prevention, and weather-aware farm decisions."
        image="https://images.unsplash.com/photo-1516253593875-bd7ba052fbc5?auto=format&fit=crop&w=1800&q=80"
      />
      <section className="page-band bg-cream">
        <div className="container-frame">
          <AssistantClient />
        </div>
      </section>
    </>
  );
}
