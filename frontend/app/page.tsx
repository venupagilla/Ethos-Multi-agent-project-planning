import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { IntroHero } from "@/components/IntroHero";
import { AboutUs } from "@/components/AboutUs";
import { BeyondInfluence } from "@/components/BeyondInfluence";
import { Services } from "@/components/Services";
import { BuildingBrands } from "@/components/BuildingBrands";
import { OurWork } from "@/components/OurWork";
import { Achievement } from "@/components/Achievement";
import { Testimonial } from "@/components/Testimonial";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-white selection:text-black">
      <Navbar />
      <main>
        <Hero />
        <section id="concept">
          <IntroHero />
        </section>
        <BeyondInfluence />
        <Services />
        <BuildingBrands />
        <section id="workflows">
          <OurWork />
        </section>
        <Achievement />
      </main>
      <Footer />
    </div>
  );
}
