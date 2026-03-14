"use client";

import { motion } from "framer-motion";
import { Button } from "./ui/Button";
import { ArrowRight } from "lucide-react";

const works = [
  {
    title: "AI-Powered E-Commerce Recommendation Engine",
    category1: "LangGraph Execution",
    category2: "Machine Learning",
    desc: "Input: 'Build a product recommendation system for our online store.' → Agent decomposed into 7 tasks (Data Pipeline, Model Training, API, UI, A/B Testing, Deployment, Monitoring), matched 4 employees by skill-set, selected PyTorch + FastAPI + Redis, and produced a full workflow DAG — zero human input.",
    image: "https://cdn.prod.website-files.com/68ff36f383b9d4f315b770ec/69017b63b09b04106e9f9c4f_Rectangle%2040187.png",
  },
  {
    title: "Enterprise HR Onboarding Automation",
    category1: "Multi-Agent",
    category2: "Process Automation",
    desc: "Input: 'Automate our new-hire onboarding.' → The system identified 9 sequential tasks, detected that 2 employees were overloaded mid-way and autonomously re-assigned, switched the document tool from Notion to Confluence after detecting an API error — all without halting the pipeline.",
    image: "https://cdn.prod.website-files.com/68ff36f383b9d4f315b770ec/69017b06ad9d262c914cef44_Rectangle%2040187-2.png",
  },
  {
    title: "Real-Time Financial Fraud Detection System",
    category1: "Adaptive Decisions",
    category2: "Backend + ML",
    desc: "Input: 'Build a fraud detection pipeline for transaction monitoring.' → Agent analyzed requirements, generated a dependency graph (Data Ingestion → Feature Eng. → Model → Alerting → Dashboard), matched the ML engineer by workload (38%), selected Kafka + XGBoost + Grafana, and estimated 12-day completion.",
    image: "https://cdn.prod.website-files.com/68ff36f383b9d4f315b770ec/69017af3f4d8d538b76680b3_Rectangle%2040187-1.png",
  }
];

function ProjectCard({ work, index }: { work: any; index: number }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      viewport={{ once: true, margin: "-100px" }}
      className="flex flex-col md:flex-row gap-12 lg:gap-24 items-center group cursor-pointer"
    >
      {/* Content Left */}
      <div className="flex-1 flex flex-col justify-between h-full order-2 md:order-1">
        <div>
          <div className="flex items-center gap-4 mb-8">
            <span className="border border-black rounded-full px-4 py-1 text-sm">{work.category1}</span>
            <span className="border border-black rounded-full px-4 py-1 text-sm">{work.category2}</span>
          </div>
          <h3 className="text-4xl lg:text-5xl font-bold tracking-tighter leading-tight mb-16 group-hover:underline underline-offset-8">
            {work.title}
          </h3>
        </div>
        
        <div className="mt-auto">
          <p className="text-lg text-gray-500 mb-8 max-w-sm">
            {work.desc}
          </p>
          <Button variant="secondary" className="rounded-full bg-black! text-white! hover:bg-black/80!">
            VIEW PROJECT <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Image Right */}
      <div className="flex-[1.5] w-full order-1 md:order-2 overflow-hidden rounded-[2.5rem]">
        {/* Simplified Parallax effect using whileInView scale */}
        <motion.img 
          initial={{ scale: 1.2 }}
          whileInView={{ scale: 1.05 }}
          whileHover={{ scale: 1.15 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          viewport={{ once: false, margin: "-100px" }}
          src={work.image} 
          alt={work.title}
          className="w-full h-[500px] lg:h-[700px] object-cover rounded-[2.5rem]"
        />
      </div>
    </motion.div>
  );
}

export function OurWork() {
  return (
    <section className="py-32 bg-white text-black min-h-screen">
      <div className="container mx-auto px-6 max-w-7xl">
        
        {/* Header Label */}
        <div className="flex flex-col items-center justify-center text-center mb-24">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-8 h-8 rounded-full border border-black/30 flex items-center justify-center">
              <div className="w-2 h-2 bg-black rounded-full"></div>
            </div>
            <span className="uppercase tracking-widest text-sm font-semibold text-black">OUR WORK</span>
          </div>

          <motion.h2 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-6xl md:text-8xl lg:text-[10rem] font-bold tracking-tighter leading-none text-black uppercase font-heading"
          >
            EXAMPLE <span className="text-blue-300">SYSTEM</span><br/>
            EXECUTIONS
          </motion.h2>
        </div>

        {/* Projects List */}
        <div className="space-y-32">
          {works.map((work, index) => (
            <ProjectCard key={index} work={work} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
