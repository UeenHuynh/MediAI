"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Activity, Lock, Mail, AlertCircle, Eye, EyeOff, CheckCircle } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/Button";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});
type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [showPass, setShowPass] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    clearError();
    const success = await login(data.username, data.password);
    if (success) router.push("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background */}
      <motion.div animate={{ scale: [1, 1.15, 1] }} transition={{ duration: 8, repeat: Infinity }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/15 rounded-full blur-[120px] pointer-events-none -z-10" />
      <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 10, repeat: Infinity, delay: 2 }}
        className="absolute top-0 right-0 w-[350px] h-[350px] bg-purple-500/15 rounded-full blur-[100px] pointer-events-none -z-10" />

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-3xl rounded-3xl overflow-hidden border border-white/[0.1] shadow-2xl grid grid-cols-2"
      >
        {/* Left panel */}
        <div className="relative bg-gradient-to-br from-blue-600/25 to-purple-700/25 backdrop-blur-xl p-10 flex flex-col justify-between">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
          <div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", delay: 0.2 }}
              className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-5 shadow-lg shadow-blue-500/25"
            >
              <Activity className="w-6 h-6 text-white" />
            </motion.div>
            <h2 className="text-2xl font-bold text-white mb-2">MediAI</h2>
            <p className="text-gray-300 text-sm leading-relaxed">
              Next-generation ICU clinical decision support system
            </p>
          </div>

          {/* ECG animation */}
          <div className="my-8">
            <svg viewBox="0 0 200 56" className="w-full opacity-60">
              <motion.path
                d="M0,28 L28,28 L36,8 L42,48 L48,28 L76,28 L84,8 L90,48 L96,28 L200,28"
                fill="none" stroke="url(#ecg-grad)" strokeWidth="2" strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
              <defs>
                <linearGradient id="ecg-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#a855f7" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div className="space-y-2.5">
            {["Role-based access control", "End-to-end encryption", "HIPAA compliant"].map((f) => (
              <div key={f} className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />{f}
              </div>
            ))}
          </div>
        </div>

        {/* Right panel */}
        <div className="bg-white/[0.05] backdrop-blur-xl p-10">
          <h3 className="text-xl font-bold text-white mb-1">Sign In</h3>
          <p className="text-gray-400 text-sm mb-8">Medical Staff Portal</p>

          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-5 p-3 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-2"
            >
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <span className="text-red-300 text-sm">{error}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Username */}
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Username
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  {...register("username")}
                  type="text"
                  placeholder="demo"
                  className={`w-full pl-9 pr-4 py-2.5 bg-white/[0.06] border rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all ${errors.username ? "border-red-500/50" : "border-white/[0.12]"}`}
                />
              </div>
              {errors.username && <p className="mt-1 text-xs text-red-400">{errors.username.message}</p>}
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  {...register("password")}
                  type={showPass ? "text" : "password"}
                  placeholder="••••••••"
                  className={`w-full pl-9 pr-10 py-2.5 bg-white/[0.06] border rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all ${errors.password ? "border-red-500/50" : "border-white/[0.12]"}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
            </div>

            <Button type="submit" className="w-full" size="lg" loading={isLoading}>
              Sign In
            </Button>
          </form>

          <div className="mt-6 pt-5 border-t border-white/[0.08] text-center">
            <p className="text-xs text-gray-500 mb-2">Demo credentials</p>
            <div className="flex justify-center gap-2">
              <code className="px-2 py-1 bg-white/[0.06] rounded-lg text-xs text-gray-300">demo</code>
              <span className="text-gray-600 text-xs flex items-center">/</span>
              <code className="px-2 py-1 bg-white/[0.06] rounded-lg text-xs text-gray-300">demo123</code>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
