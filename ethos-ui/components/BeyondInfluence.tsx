"use client";

import { motion } from "framer-motion";

export function BeyondInfluence() {
  return (
    <section className="relative bg-black text-white py-32 border-t border-white/10 overflow-hidden">
      
      {/* Background Graphic Lines to match original design */}
      <div className="absolute inset-0 z-0 opacity-20 pointer-events-none flex justify-center items-center">
        <div className="w-[1200px] h-[1200px] border border-white/20 rounded-full absolute -left-[600px]"></div>
        <div className="w-[1200px] h-[1200px] border border-white/20 rounded-full absolute -right-[600px]"></div>
      </div>

      <div className="container mx-auto px-6 max-w-7xl relative z-10">
        
        {/* First Row: Beyond Influence -> Beyond Automation */}
        <div className="flex flex-col lg:flex-row justify-between items-start gap-12 lg:gap-24 mb-32">
          <motion.h2 
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-7xl md:text-8xl lg:text-9xl font-bold tracking-tighter leading-none font-heading flex-1"
          >
            Beyond<br/>Automation
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
            className="text-xl md:text-2xl text-gray-400 max-w-lg lg:mt-4 leading-relaxed font-sans"
          >
            Automation blindly executes scripts. Autonomy reasons. The AI continuously monitors the workflow state, reassigning overloaded employees and adapting instantly to delays.
          </motion.p>
        </div>

        {/* Separator */}
        <div className="w-full h-px bg-white/10 mb-32"></div>

        {/* Second Row: And impact -> And reasoning */}
        <div className="flex flex-col lg:flex-row justify-between items-start gap-12 lg:gap-24">
          <motion.h2 
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-7xl md:text-8xl lg:text-9xl font-bold tracking-tighter leading-none font-heading flex-1 lg:pl-32"
          >
            And<br/>reasoning
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
            className="text-xl md:text-2xl text-gray-400 max-w-lg lg:mt-12 leading-relaxed font-sans"
          >
            Powered by a multi-agent LangGraph architecture, 7 distinct LLM agents collaborate to turn your simple unstructured text prompt into a fully managed, structured execution plan.
          </motion.p>
        </div>

      </div>
    </section>
  );
}
