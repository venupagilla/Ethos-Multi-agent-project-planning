"use client";

import { motion } from "framer-motion";

export function Achievement() {
  return (
    <section className="py-32 bg-black text-white px-6">
      <div className="container mx-auto max-w-7xl">
        
        {/* Background Decorative Image Top Right */}
        <div className="relative mb-24 md:mb-48">
          <motion.div 
             initial={{ opacity: 0, scale: 0.8 }}
             whileInView={{ opacity: 1, scale: 1 }}
             transition={{ duration: 1 }}
             viewport={{ once: true }}
             className="w-full md:w-3/4 mx-auto rounded-3xl overflow-hidden shadow-2xl mix-blend-screen opacity-60"
          >
            <img 
              src="https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68ff0a78b3a7e4141489a2e5_our_service%20(1).webp" 
              alt="Achievements Bg" 
              className="w-full h-[300px] md:h-[500px] object-cover"
            />
          </motion.div>
        </div>

        <div className="flex flex-col">
          {/* Header Label */}
          <div className="flex items-center gap-3 mb-16">
            <div className="w-8 h-8 rounded-full border border-white/30 flex items-center justify-center">
              <div className="w-2 h-2 bg-white rounded-full"></div>
            </div>
            <span className="uppercase tracking-widest text-sm font-semibold text-white">SYSTEM ANALYTICS</span>
          </div>

          <div className="flex flex-col lg:flex-row gap-16 justify-between items-start mb-32 border-b border-white/20 pb-16">
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-6xl md:text-8xl font-bold tracking-tighter leading-[0.9] flex-1 font-heading"
            >
              Unmatched<br/>Efficiency
            </motion.h2>

            <motion.div 
               initial={{ opacity: 0, x: 20 }}
               whileInView={{ opacity: 1, x: 0 }}
               transition={{ duration: 0.8, delay: 0.2 }}
               viewport={{ once: true }}
               className="flex-1 max-w-xl text-xl md:text-2xl text-gray-400 font-light leading-relaxed font-sans"
            >
              By replacing manual human orchestration with continuous LangGraph monitoring, we eliminate workflow bottlenecks and drastically reduce time-to-market.
            </motion.div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12 w-full">
             <motion.div 
               initial={{ opacity: 0, y: 30 }}
               whileInView={{ opacity: 1, y: 0 }}
               transition={{ duration: 0.8, delay: 0.4 }}
               viewport={{ once: true }}
               className="flex flex-col items-start p-8 rounded-3xl"
             >
               <div className="text-7xl font-bold mb-4 tracking-tighter font-heading text-blue-200">7</div>
               <div className="text-lg text-gray-400 font-sans">Specialized LLM Agents working in unison to decompose and assign tasks.</div>
             </motion.div>
             
             <motion.div 
               initial={{ opacity: 0, y: 30 }}
               whileInView={{ opacity: 1, y: 0 }}
               transition={{ duration: 0.8, delay: 0.6 }}
               viewport={{ once: true }}
               className="flex flex-col items-start p-8 rounded-3xl bg-white/5 border border-white/10"
             >
               <div className="text-7xl font-bold mb-4 tracking-tighter font-heading text-blue-200">100%</div>
               <div className="text-lg text-gray-400 font-sans">Resource optimization, ensuring workloads are balanced across human and digital tools.</div>
             </motion.div>

             <motion.div 
               initial={{ opacity: 0, y: 30 }}
               whileInView={{ opacity: 1, y: 0 }}
               transition={{ duration: 0.8, delay: 0.8 }}
               viewport={{ once: true }}
               className="flex flex-col items-start p-8 rounded-3xl"
             >
               <div className="text-7xl font-bold mb-4 tracking-tighter font-heading text-blue-200">24/7</div>
               <div className="text-lg text-gray-400 font-sans">Continuous adaptive monitoring of pipeline endpoints and failures.</div>
             </motion.div>
          </div>

        </div>
      </div>
    </section>
  );
}
