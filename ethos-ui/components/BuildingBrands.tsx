"use client";

import { motion } from "framer-motion";

export function BuildingBrands() {
  return (
    <section className="relative min-h-screen w-full flex flex-col items-center justify-center bg-black overflow-hidden py-32">
      
      {/* Background Globe Overlay */}
      <div className="absolute inset-0 z-0 flex items-center justify-center opacity-60">
        <motion.img 
          initial={{ scale: 0.8, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          transition={{ duration: 2, ease: "easeOut" }}
          viewport={{ once: true, margin: "-200px" }}
          src="https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d6015fbe8ddba0e8a71d79_A-striking-visual-concept-of-a-globe.webp"
          alt="Abstract Globe"
          className="w-[800px] h-[800px] object-cover rounded-full mix-blend-screen"
        />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center">
        
        {/* Label */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="flex items-center gap-3 mb-12"
        >
          <div className="w-8 h-8 rounded-full border border-white/30 flex items-center justify-center">
            <div className="w-2 h-2 bg-blue-200 rounded-full"></div>
          </div>
          <span className="uppercase tracking-widest text-sm font-semibold text-white">SYSTEM OBSERVABILITY</span>
        </motion.div>

        {/* Huge Text */}
        <motion.h2 
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, ease: "easeOut" }}
          viewport={{ once: true }}
          className="text-6xl md:text-8xl lg:text-[9rem] font-bold tracking-tighter leading-[0.85] text-white font-heading"
        >
          BUILDING <span className="text-blue-200">WORKFLOWS</span><br/>
          WITH 100% AUTONOMY &<br/>
          SMART AI
        </motion.h2>

      </div>
    </section>
  );
}
