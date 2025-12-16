"use client";

import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface GlassCardProps extends HTMLMotionProps<"div"> {
    children: ReactNode;
    className?: string;
    hover?: boolean;
    blur?: "sm" | "md" | "lg" | "xl";
}

export function GlassCard({
    children,
    className,
    hover = true,
    blur = "lg",
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
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            whileHover={hover ? { scale: 1.02, y: -5 } : undefined}
            className={cn(
                // Glass effect
                "bg-white/10 dark:bg-gray-900/40",
                blurClasses[blur],
                // Border
                "border border-white/20 dark:border-gray-700/50",
                // Shadow
                "shadow-xl shadow-black/5",
                // Rounded
                "rounded-2xl",
                // Padding
                "p-6",
                // Transition
                "transition-all duration-300",
                className
            )}
            {...props}
        >
            {children}
        </motion.div>
    );
}

export default GlassCard;
