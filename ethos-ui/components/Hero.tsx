"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { AnimatedText } from "./ui/AnimatedText";
import { ArrowRight } from "lucide-react";
import { useRef } from "react";

export function Hero() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "40%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  return (
    <section ref={ref} className="relative h-screen min-h-[700px] w-full overflow-hidden bg-black">
      {/* Background Video with Parallax */}
      <motion.div
        style={{ y }}
        className="absolute inset-0 z-0"
      >
        <video
          autoPlay
          loop
          muted
          playsInline
          className="object-cover w-full h-full opacity-50"
        >
          <source src="https://cdn.pixabay.com/video/2024/03/15/204306-923909642_large.mp4" type="video/mp4" />
        </video>
        {/* Gradient overlays for depth */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/80" />
      </motion.div>

      {/* Center Content */}
      <motion.div
        style={{ opacity }}
        className="relative z-10 h-full flex flex-col items-center justify-center text-center px-6"
      >
        {/* Pill Label */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="flex items-center gap-2 mb-8 px-4 py-2 rounded-full border border-white/20 bg-white/5 backdrop-blur-sm"
        >
          <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
          <span className="text-xs uppercase tracking-widest text-gray-300 font-semibold font-sans">
            Your Digital Project Manager
          </span>
        </motion.div>

        {/* Main Title */}
        <div className="overflow-hidden mb-4">
          <motion.h1
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            transition={{ duration: 1, ease: [0.33, 1, 0.68, 1], delay: 0.2 }}
            className="text-[15vw] md:text-[11vw] lg:text-[10vw] font-bold leading-[0.85] tracking-tighter text-white font-heading uppercase"
          >
            AUTONOMOUS
          </motion.h1>
        </div>
        <div className="overflow-hidden mb-12">
          <motion.h1
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            transition={{ duration: 1, ease: [0.33, 1, 0.68, 1], delay: 0.35 }}
            className="text-[15vw] md:text-[11vw] lg:text-[10vw] font-bold leading-[0.85] tracking-tighter text-white/80 font-heading uppercase"
          >
            WORKFLOW
          </motion.h1>
        </div>

        {/* Bottom Info Bar — separated by a thin rule */}
        <div className="w-full max-w-4xl border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <AnimatedText
            text="100% Autonomy. Turn a one-line project idea into a fully orchestrated AI-managed workflow — instantly."
            className="text-base md:text-lg text-gray-400 max-w-sm text-left font-sans"
            delay={12}
          />
          <motion.a
            href="#components"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
            className="flex items-center gap-2 px-6 py-3 rounded-full border border-white/30 text-white text-sm font-semibold uppercase tracking-widest hover:bg-white hover:text-black transition-all duration-300 font-sans shrink-0"
          >
            Discover Ethos <ArrowRight className="w-4 h-4" />
          </motion.a>
        </div>
      </motion.div>

      {/* Scroll Hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.8 }}
        className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 text-center text-xs tracking-[0.3em] uppercase text-gray-500 font-sans"
      >
        Scroll Down ↓
      </motion.div>
    </section>
  );
}

