"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

const services = [
  {
    num: "01",
    title: "Project Understanding",
    desc: "The AI agent analyzes the base project description using LLM reasoning to extract required skills, project complexity, and necessary toolsets.",
    img: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/69006e377ba2b0213ddca4f9_Rectangle%2040166.png"
  },
  {
    num: "02",
    title: "Task Decomposition",
    desc: "Large abstractions are broken down into actionable, sequential nodes. The agent auto-generates tasks, required dependencies, and a timeline.",
    img: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/69006e369b6aef3711ac3d82_Rectangle%2040166-1.png"
  },
  {
    num: "03",
    title: "Resource Matching",
    desc: "The system compares task requirements against your employee dataset, assessing skills, experience level, and current workload to find the optimal assignee.",
    img: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/69006e367dc11080db93c689_Rectangle%2040167.png"
  },
  {
    num: "04",
    title: "Workflow Execution",
    desc: "Tasks are connected into a live sequence. The AI assigns specific development, design, and deployment software from the tools database.",
    img: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/69006e37b579125c7e8e791b_Rectangle%2040168.png"
  },
  {
    num: "05",
    title: "Adaptive Decision Making",
    desc: "The most vital capability: autonomy. The AI continuously monitors node states, dynamically re-routing assignments if workers are overloaded or tools fail.",
    img: "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/69006e374b066a5294631817_Rectangle%2040165.png"
  }
];

export function Services() {
  const targetRef = useRef<HTMLDivElement>(null);
  
  // Horizontal scroll for desktop
  const { scrollYProgress } = useScroll({
    target: targetRef,
  });

  const x = useTransform(scrollYProgress, [0, 1], ["0%", "-60%"]);

  return (
    <section 
      ref={targetRef} 
      id="components"
      className="relative h-[250vh] bg-black text-white"
    >
      <div className="sticky top-0 flex h-screen items-center overflow-hidden">
        
        {/* Background Graphic */}
        <div className="absolute inset-0 z-0 flex items-center justify-center opacity-30 pointer-events-none">
          <img 
            src="https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/691d623691fa930a52b1dcf6_our_service%20(2).webp" 
            alt="Service Bg" 
            className="w-full max-w-[1400px] object-cover mix-blend-screen"
          />
        </div>

        <div className="container mx-auto px-6 max-w-7xl relative z-10 w-full">
          
          <div className="flex flex-col md:flex-row gap-12 w-full items-center">
            
            {/* Sticky Header Left */}
            <div className="flex-1 w-full max-w-sm shrink-0">
               <div className="flex items-center gap-3 mb-12">
                  <div className="w-8 h-8 rounded-full border border-white/30 flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <span className="uppercase tracking-widest text-sm font-semibold">Components</span>
               </div>
               
               <h2 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6">
                 5 Core<span className="text-blue-300"> Logical</span><br/>
                 Phases
               </h2>
               <p className="text-gray-400 text-lg uppercase tracking-wide">
                 Powered by LangGraph Architecture.
               </p>
            </div>

            {/* Scrolling Cards Right */}
            <div className="flex-1 w-full overflow-hidden">
               {/* Mobile view just stacks, desktop uses the framer motion transform */}
               <motion.div 
                 style={{ x }} 
                 className="flex gap-8 w-[200vw] md:w-auto"
               >
                 {services.map((service, index) => (
                   <div 
                     key={index} 
                     className="w-[300px] shrink-0 bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-sm transition-colors hover:bg-white/10"
                   >
                     <div className="text-4xl font-light text-gray-500 mb-6">{service.num}</div>
                     <h3 className="text-2xl font-bold mb-6">{service.title}</h3>
                     <img 
                       src={service.img} 
                       alt={service.title} 
                       className="w-full h-48 object-cover rounded-xl mb-6 grayscale hover:grayscale-0 transition-all duration-300"
                     />
                     <p className="text-sm leading-relaxed text-gray-400">
                       {service.desc}
                     </p>
                   </div>
                 ))}
               </motion.div>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}
