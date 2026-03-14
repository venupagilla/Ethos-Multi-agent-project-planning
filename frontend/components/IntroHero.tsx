"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export function IntroHero() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  // Parallax: Logo moves up slower than the text, creating depth.
  const logoY = useTransform(scrollYProgress, [0, 1], ["0%", "40%"]);

  return (
    <section ref={containerRef} className="relative min-h-[140vh] w-full bg-black pt-32 pb-48 text-white">
      {/* Background Graphic Lines */}
      <div className="absolute inset-0 z-0 opacity-20 pointer-events-none overflow-hidden">
        <div className="w-[900px] h-[900px] border border-white/15 rounded-full absolute left-1/2 -translate-x-1/2 top-[-200px]"></div>
        <div className="w-[600px] h-[600px] border border-white/10 rounded-full absolute left-1/2 -translate-x-1/2 top-[10%]"></div>
      </div>

      <div className="container mx-auto px-6 max-w-7xl relative z-10 flex flex-col md:flex-row justify-between items-start pt-12">
        
        {/* Left Side: Large Stacked Typography */}
        <div className="flex flex-col z-20 font-heading">
          <motion.div initial={{ opacity: 0, y: 50 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} viewport={{ once: true }} className="text-[10vw] md:text-[8vw] font-bold tracking-tighter leading-[0.9]">
            Powering<br/>
            Enterprises<br/>
            with<br/>
            Autonomous<br/>
            <span className="text-gray-400">Smart Agents</span>
          </motion.div>
        </div>

        {/* Floating 3D Logo with Parallax - always centered, never clipped */}
        <motion.div 
          style={{ y: logoY }}
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.2, delay: 0.4, type: "spring" }}
          viewport={{ once: true }}
          className="absolute top-[10%] left-1/2 -translate-x-1/2 z-30 w-[420px] h-[420px] md:w-[650px] md:h-[650px] pointer-events-none mix-blend-screen"
        >
          <img 
            src="https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68faef37f06dcd94d9065115_chrome_effect_3d_element_print_web_1.webp" 
            alt="3D Floating Model"
            className="w-full h-full object-contain filter contrast-125 brightness-110"
          />
        </motion.div>

        {/* Right Side: Paragraph and Button */}
        <div className="flex flex-col mt-32 md:mt-[30vh] max-w-md z-20 font-sans md:pl-12">
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            viewport={{ once: true }}
            className="text-xl md:text-2xl text-gray-300 leading-relaxed mb-12"
          >
            Organizations manage projects using human project managers who manually analyze requirements, assign employees, and monitor progress. We replace this bottleneck with AI reasoning capable of autonomously managing entire enterprise workflows.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            viewport={{ once: true }}
          >
            <button className="px-8 py-4 border border-white rounded-full text-sm font-semibold tracking-widest uppercase hover:bg-white hover:text-black transition-colors duration-300">
              Discover Concept
            </button>
          </motion.div>
        </div>

      </div>
    </section>
  );
}
