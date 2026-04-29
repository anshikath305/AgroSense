import {
  Bot,
  FlaskConical,
  Leaf,
  Microscope,
  Sprout,
  Wheat,
} from "lucide-react";

export const navItems = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/#features" },
  { label: "Crop AI", href: "/crop-ai" },
  { label: "Disease AI", href: "/disease-ai" },
  { label: "Fertilizer AI", href: "/fertilizer-ai" },
  { label: "Assistant", href: "/assistant" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

export const features = [
  {
    title: "Crop Recommendation",
    description:
      "Match NPK, pH, rainfall, temperature, and humidity to the most suitable crop for the field.",
    href: "/crop-ai",
    icon: Sprout,
  },
  {
    title: "Disease Detection",
    description:
      "Upload a leaf image and get a plant health readout with treatment and prevention guidance.",
    href: "/disease-ai",
    icon: Microscope,
  },
  {
    title: "Fertilizer AI",
    description:
      "Predict fertilizer type and quantity from crop, soil, moisture, and nutrient conditions.",
    href: "/fertilizer-ai",
    icon: FlaskConical,
  },
  {
    title: "Advisory Assistant",
    description:
      "Ask practical farming questions and receive clear, field-ready recommendations.",
    href: "/assistant",
    icon: Bot,
  },
];

export const howItWorks = [
  "Enter soil, crop, image, or question inputs.",
  "AgroSense routes the request to the correct AI model.",
  "Results return as clear recommendations with next actions.",
];

export const benefits = [
  { metric: "5x", label: "Faster crop health triage" },
  { metric: "30%", label: "More efficient input planning" },
  { metric: "24/7", label: "AI advisory availability" },
  { metric: "4", label: "Core farming intelligence tools" },
];

export const testimonials = [
  {
    quote:
      "AgroSense turns technical soil and leaf data into decisions our field team can act on quickly.",
    name: "Anika Rao",
    role: "Farm operations lead",
  },
  {
    quote:
      "The disease scan flow is simple enough for field staff but detailed enough for agronomists.",
    name: "Rohan Mehta",
    role: "Horticulture consultant",
  },
  {
    quote:
      "The fertilizer recommendation page helped us standardize planning across different plots.",
    name: "Maya Singh",
    role: "Cooperative manager",
  },
];

export const cropExamples = [
  { label: "Rice field", values: [90, 42, 43, 22, 82, 6.5, 202] },
  { label: "Cotton plot", values: [117, 46, 19, 25, 79, 7.8, 90] },
  { label: "Chickpea soil", values: [40, 72, 77, 18, 16, 7.3, 89] },
];

export const soilTypes = ["Black", "Clayey", "Loamy", "Red", "Sandy"];

export const cropTypes = [
  "Barley",
  "Cotton",
  "Ground Nuts",
  "Maize",
  "Millets",
  "Oil seeds",
  "Paddy",
  "Pulses",
  "Sugarcane",
  "Tobacco",
  "Wheat",
];

export const assistantPrompts = [
  "Why are my leaves yellow?",
  "Best fertilizer for wheat?",
  "How to stop pest attack?",
  "What should I do after heavy rainfall?",
];

export const heroStats = [
  { icon: Leaf, label: "Crop AI", value: "22 crops" },
  { icon: Wheat, label: "Soil inputs", value: "NPK + pH" },
  { icon: Bot, label: "Advisory", value: "Multilingual ready" },
];
