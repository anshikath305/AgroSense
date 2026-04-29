import { FertilizerPredictionClient } from "@/components/FertilizerPredictionClient";
import { PageHero } from "@/components/PageHero";

export default function FertilizerAiPage() {
  return (
    <>
      <PageHero
        eyebrow="Fertilizer Prediction"
        title="Plan nutrients with a smarter soil and crop dashboard."
        description="Submit crop type, soil type, moisture, weather, and nutrient readings to predict fertilizer type, quantity, and usage guidance."
        image="https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&w=1800&q=80"
      />
      <section className="page-band bg-cream">
        <div className="container-frame">
          <FertilizerPredictionClient />
        </div>
      </section>
    </>
  );
}
