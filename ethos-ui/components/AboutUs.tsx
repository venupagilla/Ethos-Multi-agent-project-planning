"use client";

import { motion } from "framer-motion";
import { Button } from "./ui/Button";

const brands = [
  "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d60c1ea8eb64fe39494266_Fictional%20company%20logo-2.svg",
  "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d60c1e9b884d555d5c423a_Fictional%20company%20logo.svg",
  "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d60c1e6da9b951eefc9623_Fictional%20company%20logo-1.svg",
  "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68d60c1ec38fca6221532b4a_Fictional%20company%20logo-3.svg",
  "https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68fafaa0b5b4a9e3ed268395_Fictional%20company%20logo%20(1).svg",
];

export function AboutUs() {
  return (
    <section className="relative py-32 bg-black text-white overflow-hidden border-t border-white/10">
      
      {/* Background abstract shape (approximated) */}
      <div className="absolute top-0 right-0 opacity-20 pointer-events-none">
        <img 
          src="https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68fafb49f3a747a3e36929dd_Frame%202147237039%20(1).svg" 
          alt="decoration" 
          className="w-[800px] h-[800px] object-cover"
        />
      </div>

      <div className="container mx-auto px-6 max-w-7xl relative z-10">
        
        {/* Header Label */}
        <div className="flex items-center gap-3 mb-16 justify-center md:justify-start">
          <div className="w-8 h-8 rounded-full border border-white/30 flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full"></div>
          </div>
          <span className="uppercase tracking-widest text-sm font-semibold">About Us</span>
        </div>

        {/* Main Content Area */}
        <div className="flex flex-col md:flex-row gap-16 lg:gap-32 items-center">
          
          <div className="flex-1 w-full relative">
            {/* Center 3D Object Illustration */}
            {/* <motion.div 
              initial={{ scale: 0.8, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1, type: "spring" }}
              viewport={{ once: true, margin: "-100px" }}
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-0 opacity-50 md:opacity-100 mix-blend-screen"
            >
              <img 
                src="https://cdn.prod.website-files.com/68d5ef256aa1426c46f24ec9/68faef37f06dcd94d9065115_chrome_effect_3d_element_print_web_1.webp" 
                alt="3D chrome element"
                className="w-64 md:w-96 drop-shadow-2xl grayscale"
              />
            </motion.div> */}

            <motion.h2 
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-5xl md:text-7xl lg:text-8xl font-bold leading-tight tracking-tighter relative z-10 text-center md:text-left mix-blend-difference"
            >
              Powering Brands<br/>
              with Imagination<br/>
              <span className="text-gray-400">Bold Impact</span>
            </motion.h2>
          </div>

          <motion.div 
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
            className="flex-1 max-w-xl text-center md:text-left relative z-10"
          >
            <p className="text-xl md:text-2xl text-gray-400 mb-10 leading-relaxed font-light">
              We came together with a single vision to create brands that inspire and designs that leave a lasting impression. What started as a small group of passionate creatives has grown into an award-winning agency, dedicated to turning ideas into meaningful experiences.
            </p>
            <Button variant="outline" className="rounded-full">
              Read More
            </Button>
          </motion.div>
        </div>
      </div>

      {/* Marquee Section */}
      <div className="mt-32 w-full overflow-hidden flex border-y border-white/10 py-10 bg-black z-20 relative">
        <motion.div
          animate={{ x: [0, -1000] }}
          transition={{
            repeat: Infinity,
            repeatType: "loop",
            duration: 20,
            ease: "linear",
          }}
          className="flex space-x-16 md:space-x-32 flex-shrink-0 px-8"
        >
          {/* Output 3 lists to ensure smooth scrolling */}
          {[...brands, ...brands, ...brands].map((logo, index) => (
            <img 
              key={index} 
              src={logo} 
              alt="Brand logo" 
              className="h-8 md:h-12 opacity-50 hover:opacity-100 transition-opacity invert"
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
