"use client";

import { motion } from "framer-motion";
import { cn } from "@/app/lib/utils";
import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "outline";
  className?: string;
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, variant = "primary", className, asChild = false, ...props }, ref) => {
    const baseStyles =
      "relative inline-flex items-center justify-center overflow-hidden rounded-full font-medium transition-all duration-300 ease-out";
      
    const variants = {
      primary: "bg-white text-black hover:bg-gray-200 py-3 px-6",
      secondary: "bg-black text-white hover:bg-gray-900 border border-white/20 py-3 px-6",
      outline: "bg-transparent text-white border border-white hover:bg-white/10 py-3 px-6",
    };

    const MotionButton = asChild ? motion.div : motion.button;

    return (
      <MotionButton
        ref={ref as any}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={cn(baseStyles, variants[variant], className)}
        {...(props as any)}
      >
        <span className="relative z-10 flex items-center gap-2 uppercase tracking-wide text-sm font-semibold">
          {children}
        </span>
      </MotionButton>
    );
  }
);

Button.displayName = "Button";
