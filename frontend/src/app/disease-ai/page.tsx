import { DiseaseDetectionClient } from "@/components/DiseaseDetectionClient";
import { PageHero } from "@/components/PageHero";

export default function DiseaseAiPage() {
  return (
    <>
      <PageHero
        eyebrow="Plant Disease Detection"
        title="Scan crop leaves and get treatment guidance fast."
        description="Upload a leaf image to run disease prediction, confidence scoring, treatment suggestions, prevention tips, and AI advisory in one flow."
        image="https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1800&q=80"
      />
      <section className="page-band bg-cream">
        <div className="container-frame">
          <DiseaseDetectionClient />
        </div>
      </section>
    </>
  );
}
