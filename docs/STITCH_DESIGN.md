---
name: AgroSense
colors:
  surface: '#fbf9f4'
  surface-dim: '#dbdad5'
  surface-bright: '#fbf9f4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3ee'
  surface-container: '#f0eee9'
  surface-container-high: '#eae8e3'
  surface-container-highest: '#e4e2dd'
  on-surface: '#1b1c19'
  on-surface-variant: '#414846'
  inverse-surface: '#30312e'
  inverse-on-surface: '#f2f1ec'
  outline: '#717976'
  outline-variant: '#c1c8c4'
  surface-tint: '#43655c'
  primary: '#01261f'
  on-primary: '#ffffff'
  primary-container: '#1a3c34'
  on-primary-container: '#83a69c'
  inverse-primary: '#aacec3'
  secondary: '#7b5800'
  on-secondary: '#ffffff'
  secondary-container: '#ffc95e'
  on-secondary-container: '#755400'
  tertiary: '#1e2313'
  on-tertiary: '#ffffff'
  tertiary-container: '#333827'
  on-tertiary-container: '#9ca18b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c5eadf'
  primary-fixed-dim: '#aacec3'
  on-primary-fixed: '#00201a'
  on-primary-fixed-variant: '#2b4d44'
  secondary-fixed: '#ffdea5'
  secondary-fixed-dim: '#f3be54'
  on-secondary-fixed: '#261900'
  on-secondary-fixed-variant: '#5d4200'
  tertiary-fixed: '#e0e5cc'
  tertiary-fixed-dim: '#c4c9b1'
  on-tertiary-fixed: '#191d0e'
  on-tertiary-fixed-variant: '#444937'
  background: '#fbf9f4'
  on-background: '#1b1c19'
  surface-variant: '#e4e2dd'
typography:
  display-lg:
    fontFamily: Newsreader
    fontSize: 64px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Newsreader
    fontSize: 40px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1440px
  gutter: 24px
  margin-edge: 48px
  glass-padding: 32px
---

## Brand & Style

The design system is defined by a "Biophilic-Futurism" aesthetic. It balances the raw, organic beauty of large-scale agriculture with the precision of high-tech data analytics. The goal is to evoke a sense of calm authority and premium stewardship.

The visual style utilizes **Glassmorphism** as a functional bridge between data and nature. By placing high-blur, semi-transparent interface containers over immersive, full-screen landscapes, the UI feels lightweight and non-intrusive. The interaction model is inspired by **Minimalism**, stripping away unnecessary chrome to focus on the clarity of the earth and the insights derived from it. Organic shapes—reminiscent of topography and leaf structures—soften the technical nature of the platform, ensuring it remains grounded and approachable.

## Colors

The palette is derived directly from the agricultural lifecycle. 

- **Primary (Forest Green):** A deep, saturated green used for primary branding, navigation backgrounds, and high-level structural elements. It represents density and growth.
- **Secondary (Sunset Gold):** A vibrant gold used sparingly for highlights, primary calls to action, and critical data points. It symbolizes the energy of the sun and premium value.
- **Tertiary (Moss & Earth):** Muted greens and browns serve as accent colors for categorization and secondary data visualizations.
- **Surface (Cream/Off-White):** A soft, warm neutral used for content cards and backgrounds to avoid the clinical feel of pure white, ensuring the interface feels organic and high-end.
- **Success/Warning/Error:** Integrated using natural variants (e.g., sapling green for success, terracotta for errors).

## Typography

This design system employs a sophisticated serif-sans pairing to communicate both heritage and innovation.

- **Headlines:** Use **Newsreader**. This serif typeface provides the "characterful" and "authoritative" feel required for a premium brand. Its slightly literary quality evokes the timeless nature of land ownership and agricultural wisdom.
- **Body & Data:** Use **Inter**. Chosen for its exceptional legibility in data-heavy environments. It provides a clean, systematic contrast to the serif headings.
- **Usage:** Headlines should use tighter tracking and larger scales to dominate the "Adler-style" hero sections. Labels should often be uppercase with slight letter spacing to maintain a modern, technical feel.

## Layout & Spacing

The layout utilizes a **Fixed Grid** philosophy for content containers, centered over full-bleed immersive backgrounds. 

- **The Framed Grid:** Main content is housed within a 12-column grid with a maximum width of 1440px. Large 48px outer margins create a "frame" effect, allowing the background photography to peek through the edges, enhancing the immersive feel.
- **Vertical Rhythm:** A strict 8px baseline grid ensures alignment. Use generous padding (32px+) within glassmorphic cards to create a sense of luxury and "breathability."
- **Visual Structure:** Use asymmetrical layouts for hero sections—positioning key metrics or navigation in structured floating panels while leaving the majority of the frame open for high-quality agricultural imagery.

## Elevation & Depth

Depth in this design system is achieved through **optical transparency** rather than heavy shadows.

- **Backdrop Blur:** All primary UI containers must use a `backdrop-filter: blur(20px)`. This creates a frosted-glass effect that makes the text legible without completely obscuring the landscape behind it.
- **Layering:** 
    - **Base Layer:** Full-screen photography.
    - **Mid Layer:** Semi-transparent Forest Green or Cream panels (20-60% opacity).
    - **Top Layer:** Solid text, icons, and buttons.
- **Outlines:** Instead of shadows, use "Ghost Borders"—1px solid strokes with low opacity (e.g., White at 15%)—to define the edges of glass containers. This maintains a crisp, futuristic look.

## Shapes

The shape language is **Organic yet Structured**.

- **Radius:** A consistent 1rem (16px) radius is applied to all primary cards and containers, providing a soft, approachable feel.
- **Organic Accents:** For decorative elements or secondary image masks, use non-perfect "blob" shapes or rounded polygons that mimic plot lines or leaves.
- **Interactive Elements:** Buttons and input fields follow a refined `rounded-lg` (16px) style, while small badges/tags can be pill-shaped to differentiate them from functional inputs.

## Components

- **Glass Cards:** The core container. Must feature the `backdrop-blur`, a soft tint of the Primary color (if dark) or Surface color (if light), and a subtle 1px border.
- **Primary Buttons:** High-contrast Sunset Gold background with Forest Green text. Use bold sans-serif (Inter) for the label. No shadows; use a subtle scale-down effect on press.
- **Secondary Buttons:** Ghost style with a Forest Green or White border and high-blur background.
- **Inputs:** Minimalist bottom-border only or very light glass fills. Labels should float above the field in Inter (600 weight).
- **Data Visualization:** Charts should use a palette of Moss, Sage, and Gold. Lines should be smoothed (interpolation) rather than jagged to match the organic theme.
- **Navigation:** A floating top-bar or "Adler-style" sidebar that uses high transparency, ensuring it feels like part of the environment rather than a separate header.
- **Metric Chips:** Small, semi-transparent pills used to display weather, soil health, or crop status at a glance.