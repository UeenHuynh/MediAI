"use client";

import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";
import { Loader2 } from "lucide-react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
    size?: "sm" | "md" | "lg";
    loading?: boolean;
    icon?: React.ReactNode;
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
            ...props
        },
        ref
    ) => {
        const variants = {
            primary:
                "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg shadow-blue-500/25",
            secondary:
                "bg-gray-800 text-white hover:bg-gray-700 border border-gray-700",
            outline:
                "border-2 border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white",
            ghost: "text-gray-300 hover:bg-white/10 hover:text-white",
            danger:
                "bg-gradient-to-r from-red-600 to-pink-600 text-white hover:from-red-700 hover:to-pink-700",
        };

        const sizes = {
            sm: "px-3 py-1.5 text-sm",
            md: "px-5 py-2.5 text-base",
            lg: "px-8 py-3 text-lg",
        };

        return (
            <button
                ref={ref}
                className={cn(
                    // Base styles
                    "inline-flex items-center justify-center gap-2",
                    "font-medium rounded-xl",
                    "transition-all duration-200",
                    "hover:scale-[1.02] active:scale-[0.98]",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900",
                    "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
                    // Variant & size
                    variants[variant],
                    sizes[size],
                    className
                )}
                disabled={disabled || loading}
                {...props}
            >
                {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                ) : icon ? (
                    icon
                ) : null}
                {children}
            </button>
        );
    }
);

Button.displayName = "Button";

export { Button };
export default Button;
