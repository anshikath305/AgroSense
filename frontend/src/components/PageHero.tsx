import Image from "next/image";

type PageHeroProps = {
  eyebrow: string;
  title: string;
  description: string;
  image: string;
};

export function PageHero({ eyebrow, title, description, image }: PageHeroProps) {
  return (
    <section className="relative isolate overflow-hidden bg-primary text-white">
      <Image
        src={image}
        alt=""
        fill
        sizes="100vw"
        className="-z-20 object-cover opacity-40"
      />
      <div className="absolute inset-0 -z-10 bg-primary/[0.72]" />
      <div className="container-frame py-20 md:py-24">
        <p className="mb-4 text-xs font-bold uppercase tracking-widest text-gold">
          {eyebrow}
        </p>
        <h1 className="max-w-4xl font-serif text-5xl font-semibold md:text-6xl">
          {title}
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-mint">
          {description}
        </p>
      </div>
    </section>
  );
}
