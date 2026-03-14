"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const testimonials = [
  {
    name: "Elena Rostova",
    role: "VP of Engineering",
    text: "“Deploying Ethos was a paradigm shift. The AI agent seamlessly integrated into our backend, reducing manual task delegation time by 90%.”",
    image: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/6916c743be5d0455ce825f9a_frame_2087326985%20(1).webp",
    logo: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d60c1ea8eb64fe39494266_Fictional%20company%20logo-2.svg"
  },
  {
    name: "Marcus Chen",
    role: "Project Management Lead",
    text: "“I used to spend 20 hours a week just matching employee skills to Jira tickets. Ethos's Resource Matching component automates this with 100% accuracy.”",
    image: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/6916c876663c97bc51708f49_frame_2087326985%20(2).webp",
    logo: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d60c1e9b884d555d5c423a_Fictional%20company%20logo.svg"
  },
  {
    name: "Sarah Jenkins",
    role: "Operations Director",
    text: "“The Adaptive Decision Making is what sold us. When our AWS pipeline delayed a task, the agent instantly reassigned resources to prevent a bottleneck.”",
    image: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/6916c8f1e229be3aba71badb_frame_2087326985%20(3).webp",
    logo: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d60c1e6da9b951eefc9623_Fictional%20company%20logo-1.svg"
  }
];

export function Testimonial() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <section className="py-32 bg-black text-white">
      <div className="container mx-auto px-6 max-w-7xl">
        
        {/* Main Testimonial Card */}
        <div className="relative rounded-[2.5rem] overflow-hidden min-h-[600px] flex items-end mb-12 p-8 md:p-16">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, scale: 1.05 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6, ease: "easeInOut" }}
              className="absolute inset-0 z-0 bg-cover bg-center"
              style={{ backgroundImage: `url(${testimonials[activeTab].image})` }}
            >
               {/* Dark overlay for readability */}
               <div className="absolute inset-0 bg-linear-to-t from-black/90 via-black/40 to-transparent"></div>
            </motion.div>
          </AnimatePresence>

          <div className="relative z-10 w-full flex flex-col md:flex-row gap-12 justify-between items-end">
             
             {/* Text Content */}
             <div className="flex-1 max-w-2xl">
                <div className="flex items-center gap-3 mb-8">
                  <div className="w-8 h-8 rounded-full border border-white/30 flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <span className="uppercase tracking-widest text-sm font-semibold">TESTIMONIAL</span>
                </div>
                
                <AnimatePresence mode="wait">
                  <motion.p
                    key={`text-${activeTab}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.4 }}
                    className="text-2xl md:text-4xl font-light leading-snug mb-8"
                  >
                    {testimonials[activeTab].text}
                  </motion.p>
                </AnimatePresence>
             </div>

             {/* Author Info */}
             <div className="shrink-0 text-left md:text-right">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={`author-${activeTab}`}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.4 }}
                  >
                    <div className="text-xl md:text-2xl font-bold mb-2">{testimonials[activeTab].name}</div>
                    <div className="text-gray-400">{testimonials[activeTab].role}</div>
                  </motion.div>
                </AnimatePresence>
             </div>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex justify-center gap-4 md:gap-8 flex-wrap">
          {testimonials.map((testi, i) => (
            <button
              key={i}
              onClick={() => setActiveTab(i)}
              className={`p-4 rounded-2xl border transition-all duration-300 ${
                activeTab === i 
                  ? "border-white bg-white/10" 
                  : "border-white/20 hover:border-white/50 bg-transparent"
              }`}
            >
              <img 
                src={testi.logo} 
                alt="Brand Logo" 
                className={`h-8 transition-all ${activeTab === i ? "invert opacity-100" : "invert opacity-50"}`}
              />
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
