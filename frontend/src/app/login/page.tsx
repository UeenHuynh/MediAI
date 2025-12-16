"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Activity, Lock, Mail, AlertCircle } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";

const loginSchema = z.object({
    username: z.string().min(1, "Username is required"),
    password: z.string().min(1, "Password is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const router = useRouter();
    const { login, isLoading, error, clearError } = useAuthStore();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormData) => {
        clearError();
        const success = await login(data.username, data.password);
        if (success) {
            router.push("/dashboard");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-4">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/30 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/30 rounded-full blur-3xl" />
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 w-full max-w-md"
            >
                <GlassCard className="p-8">
                    {/* Logo */}
                    <div className="flex flex-col items-center mb-8">
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", delay: 0.2 }}
                            className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-blue-500/25"
                        >
                            <Activity className="w-8 h-8 text-white" />
                        </motion.div>
                        <h1 className="text-2xl font-bold text-white">MediAI</h1>
                        <p className="text-gray-400 text-sm mt-1">
                            ICU Risk Prediction System
                        </p>
                    </div>

                    {/* Error Alert */}
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3"
                        >
                            <AlertCircle className="w-5 h-5 text-red-400" />
                            <span className="text-red-300 text-sm">{error}</span>
                        </motion.div>
                    )}

                    {/* Login Form */}
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        {/* Username */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    {...register("username")}
                                    type="text"
                                    placeholder="demo"
                                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                />
                            </div>
                            {errors.username && (
                                <p className="mt-1 text-sm text-red-400">
                                    {errors.username.message}
                                </p>
                            )}
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    {...register("password")}
                                    type="password"
                                    placeholder="••••••••"
                                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                />
                            </div>
                            {errors.password && (
                                <p className="mt-1 text-sm text-red-400">
                                    {errors.password.message}
                                </p>
                            )}
                        </div>

                        {/* Submit */}
                        <Button
                            type="submit"
                            className="w-full"
                            size="lg"
                            loading={isLoading}
                        >
                            Sign In
                        </Button>
                    </form>

                    {/* Demo credentials */}
                    <div className="mt-6 pt-6 border-t border-white/10">
                        <p className="text-center text-gray-400 text-sm">
                            Demo credentials:
                        </p>
                        <p className="text-center text-gray-300 text-sm mt-1">
                            <code className="px-2 py-1 bg-white/5 rounded">demo</code> /{" "}
                            <code className="px-2 py-1 bg-white/5 rounded">demo123</code>
                        </p>
                    </div>
                </GlassCard>
            </motion.div>
        </div>
    );
}
