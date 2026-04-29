import { CropRecommendationClient } from "@/components/CropRecommendationClient";
import { PageHero } from "@/components/PageHero";

export default function CropAiPage() {
  return (
    <>
      <PageHero
        eyebrow="Crop Recommendation Engine"
        title="Choose the right crop for the field in front of you."
        description="Enter NPK, temperature, humidity, pH, and rainfall to get a model-ranked crop recommendation with confidence and agronomic context."
        image="https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?auto=format&fit=crop&w=1800&q=80"
      />
      <section className="page-band bg-cream">
        <div className="container-frame">
          <CropRecommendationClient />
        </div>
      </section>
    </>
  );
}
