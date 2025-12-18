"use client";

import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";
import { Loader2 } from "lucide-react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
    size?: "sm" | "md" | "lg";
    loading?: boolean;
    icon?: React.ReactNode;
    glow?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            className,
            variant = "primary",
            size = "md",
            loading = false,
            icon,
            children,
            disabled,
            glow = false,
            ...props
        },
        ref
    ) => {
        const variants = {
            primary:
                "bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:shadow-xl",
            secondary:
                "bg-white/10 text-white hover:bg-white/20 border border-white/20 backdrop-blur-sm",
            outline:
                "border-2 border-purple-500/50 text-purple-300 hover:bg-purple-500/20 hover:border-purple-400 hover:text-white",
            ghost: "text-gray-300 hover:bg-white/10 hover:text-white",
            danger:
                "bg-gradient-to-r from-red-600 via-pink-600 to-rose-600 text-white shadow-lg shadow-red-500/30 hover:shadow-red-500/50",
        };

        const sizes = {
            sm: "px-4 py-2 text-sm",
            md: "px-6 py-2.5 text-base",
            lg: "px-8 py-3.5 text-lg",
        };

        return (
            <button
                ref={ref}
                className={cn(
                    // Base styles
                    "relative inline-flex items-center justify-center gap-2",
                    "font-semibold rounded-xl",
                    "transition-all duration-300 ease-out",
                    "hover:scale-[1.03] active:scale-[0.97]",
                    "focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:ring-offset-2 focus:ring-offset-transparent",
                    "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
                    // Overflow for shimmer effect
                    "overflow-hidden",
                    // Variant & size
                    variants[variant],
                    sizes[size],
                    // Glow effect
                    glow && "animate-pulse",
                    className
                )}
                disabled={disabled || loading}
                {...props}
            >
                {/* Shimmer effect overlay */}
                <span className="absolute inset-0 overflow-hidden rounded-xl">
                    <span className="absolute inset-0 -translate-x-full group-hover:animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                </span>

                {/* Button content */}
                <span className="relative flex items-center gap-2">
                    {loading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : icon ? (
                        icon
                    ) : null}
                    {children}
                </span>

                {/* Top highlight */}
                <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
            </button>
        );
    }
);

Button.displayName = "Button";

export { Button };
export default Button;

