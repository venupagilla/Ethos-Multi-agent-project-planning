"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-black text-white pt-32 pb-12 border-t border-white/10">
      <div className="container mx-auto px-6 max-w-7xl">
        
        {/* Top Links & Info */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-24 gap-8">
           <div className="flex items-center gap-4">
             <span className="text-gray-500 uppercase tracking-widest text-sm">Call Today :</span>
             <span className="font-medium">+62 523 735 1221</span>
           </div>
           <div className="hidden md:block w-px h-8 bg-white/20"></div>
           <div className="flex items-center gap-4">
             <span className="text-gray-500 uppercase tracking-widest text-sm">Email :</span>
             <span className="font-medium">deploy@ethos.ai</span>
           </div>
           <div className="hidden md:block w-px h-8 bg-white/20"></div>
           <div className="flex items-center gap-4">
             <span className="text-gray-500 uppercase tracking-widest text-sm">System :</span>
             <span className="font-medium">status.ethos.ai</span>
           </div>
        </div>

        <div className="w-full h-px bg-white/20 mb-24"></div>

        {/* Huge Let's Talk CTA */}
        <Link href="/contact" className="block text-center group cursor-pointer mb-32 relative overflow-hidden py-12">
          <motion.h2 
            whileHover={{ letterSpacing: "5px" }}
            transition={{ duration: 0.4 }}
            className="text-6xl md:text-[10rem] font-bold bg-clip-text text-white relative z-10 font-heading tracking-widest"
          >
            DEPLOY-ETHOS
          </motion.h2>

          {/* Hover Image Reveal effect (Simplified) */}
          <div className="absolute inset-0 bg-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-center justify-center z-0 pointer-events-none">
            <div className="w-64 h-64 rounded-full overflow-hidden blur-xl bg-blue-500/30"></div>
          </div>
        </Link>

        {/* Bottom Footer Area */}
        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-white/10 gap-8">
          
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <div><span className="text-white">Designed by</span> Vektora</div>
            <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
            <div><span className="text-white">Powered by</span> Webflow (Next.js Port)</div>
          </div>

          <div className="flex items-center gap-6">
            {['Twitter', 'Instagram', 'LinkedIn', 'Dribbble'].map((social) => (
              <a key={social} href="#" className="text-sm font-medium hover:text-gray-400 transition-colors uppercase tracking-widest">
                {social}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-6 text-sm text-gray-400">
            <a href="#" className="hover:text-white transition-colors">Style guide</a>
            <a href="#" className="hover:text-white transition-colors">Licenses</a>
            <a href="#" className="hover:text-white transition-colors">Changelog</a>
          </div>

        </div>
      </div>
    </footer>
  );
}
