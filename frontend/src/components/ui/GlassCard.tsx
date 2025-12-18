"use client";

import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface GlassCardProps extends HTMLMotionProps<"div"> {
    children: ReactNode;
    className?: string;
    hover?: boolean;
    blur?: "sm" | "md" | "lg" | "xl";
    glow?: boolean;
}

export function GlassCard({
    children,
    className,
    hover = true,
    blur = "xl",
    glow = false,
    ...props
}: GlassCardProps) {
    const blurClasses = {
        sm: "backdrop-blur-sm",
        md: "backdrop-blur-md",
        lg: "backdrop-blur-lg",
        xl: "backdrop-blur-xl",
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
                duration: 0.5,
                ease: [0.16, 1, 0.3, 1],
                opacity: { duration: 0.4 }
            }}
            whileHover={
                hover
                    ? {
                        scale: 1.02,
                        y: -8,
                        transition: { duration: 0.2, ease: "easeOut" },
                    }
                    : undefined
            }
            className={cn(
                // Glass effect with enhanced blur
                "bg-white/[0.08]",
                blurClasses[blur],
                // Border with subtle glow
                "border border-white/[0.15]",
                // Enhanced shadow with depth
                "shadow-[0_8px_32px_rgba(0,0,0,0.4)]",
                "shadow-black/20",
                // Rounded corners
                "rounded-2xl",
                // Padding
                "p-6",
                // Smooth transitions
                "transition-all duration-300 ease-out",
                // Inner glow highlight
                "relative overflow-hidden",
                // Glow effect on hover
                glow && "hover:shadow-[0_0_40px_rgba(139,92,246,0.3)]",
                className
            )}
            style={{
                boxShadow: glow
                    ? "0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)"
                    : "0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05)",
            }}
            {...props}
        >
            {/* Top highlight line */}
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            {/* Content */}
            {children}
        </motion.div>
    );
}

export default GlassCard;

