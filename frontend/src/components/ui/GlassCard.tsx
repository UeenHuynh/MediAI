"use client";

import { cn } from "@/lib/utils";
import { ReactNode, HTMLAttributes } from "react";

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
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
    blur = "md",   // giảm từ xl → md để nhẹ GPU hơn
    glow = false,
    onClick,
    ...props
}: GlassCardProps) {
    const blurClasses = {
        sm: "backdrop-blur-sm",
        md: "backdrop-blur-md",
        lg: "backdrop-blur-lg",
        xl: "backdrop-blur-xl",
    };

    return (
        <div
            onClick={onClick}
            className={cn(
                "bg-white/[0.08]",
                blurClasses[blur],
                "border border-white/[0.15]",
                "rounded-2xl p-6",
                "relative overflow-hidden",
                // Hover: CSS only, không dùng Framer Motion → mượt hơn nhiều
                hover && onClick && "cursor-pointer transition-transform duration-200 ease-out hover:-translate-y-1 hover:scale-[1.01]",
                hover && !onClick && "transition-transform duration-200 ease-out hover:-translate-y-1",
                glow && "hover:shadow-[0_0_30px_rgba(139,92,246,0.2)]",
                className
            )}
            style={{
                boxShadow: glow
                    ? "0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)"
                    : "0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05)",
                willChange: "transform",   // hint GPU layer
            }}
            {...props}
        >
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            {children}
        </div>
    );
}

export default GlassCard;

