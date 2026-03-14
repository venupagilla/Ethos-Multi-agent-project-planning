"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-black text-white pt-32 pb-12 border-t border-white/10">
      <div className="container mx-auto px-6 max-w-7xl">
        
        {/* Top Info Area */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-24 gap-8">
           <div className="flex items-center gap-4">
             <span className="text-gray-500 uppercase tracking-widest text-sm">Contact :</span>
             <span className="font-medium">contact@ethos.ai</span>
           </div>
           <div className="hidden md:block w-px h-8 bg-white/20"></div>
           <div className="flex items-center gap-4">
             <span className="text-gray-500 uppercase tracking-widest text-sm">System Status :</span>
             <span className="font-medium text-blue-400">Operational</span>
           </div>
        </div>

        <div className="w-full h-px bg-white/20 mb-24"></div>

        {/* Huge Ethos CTA */}
        <div className="block text-center group mb-32 relative overflow-hidden py-12">
          <motion.h2 
            initial={{ y: 20, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            className="text-6xl md:text-[10rem] font-bold bg-clip-text text-white relative z-10 font-heading tracking-widest uppercase"
          >
            ETHOS
          </motion.h2>

          <div className="absolute inset-0 bg-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-center justify-center z-0 pointer-events-none">
            <div className="w-64 h-64 rounded-full overflow-hidden blur-xl bg-blue-500/20"></div>
          </div>
        </div>

        {/* Bottom Footer Area */}
        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-white/10 gap-8">
          
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <div><span className="text-white">Ethos</span> © 2026</div>
            <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
            <div>Autonomous Project Orchestration</div>
          </div>

          <div className="flex items-center gap-6">
            {['Twitter', 'LinkedIn', 'GitHub'].map((social) => (
              <a key={social} href="#" className="text-sm font-medium hover:text-white transition-colors uppercase tracking-widest text-gray-400">
                {social}
              </a>
            ))}
          </div>

        </div>
      </div>
    </footer>
  );
}
