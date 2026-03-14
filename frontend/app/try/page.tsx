"use client";

import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { AgentDashboard } from "@/components/AgentDashboard";
import { motion } from "framer-motion";

export default function TryPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-white selection:text-black">
      <Navbar />
      <main className="pt-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <AgentDashboard />
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}
