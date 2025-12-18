"use client";

import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { ArrowRight, Activity, Brain, Shield } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/20 rounded-full blur-[120px] -z-10" />
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-purple-500/20 rounded-full blur-[100px] -z-10" />

      <main className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Column: Hero Text */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="space-y-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span className="text-sm font-medium text-gray-300">System Operational</span>
          </div>

          <h1 className="text-5xl lg:text-7xl font-bold tracking-tight text-white glow-text">
            Medi<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">AI</span>
            <br />
            <span className="text-4xl lg:text-6xl text-gray-400">Next-Gen Healthcare</span>
          </h1>

          <p className="text-xl text-gray-300 leading-relaxed max-w-xl">
            Advanced AI-powered diagnostics and mortality prediction system for modern ICUs.
          </p>

          <div className="flex flex-wrap gap-4">
            <Link href="/login">
              <Button size="lg" glow icon={<ArrowRight className="w-5 h-5" />}>
                Get Started
              </Button>
            </Link>
            <Link href="/doctors">
              <Button variant="outline" size="lg">
                View Specialists
              </Button>
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-6 pt-8 border-t border-white/10">
            <div>
              <p className="text-3xl font-bold text-white">99%</p>
              <p className="text-sm text-gray-400">Accuracy</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-white">24/7</p>
              <p className="text-sm text-gray-400">Monitoring</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-white">50+</p>
              <p className="text-sm text-gray-400">Specialists</p>
            </div>
          </div>
        </motion.div>

        {/* Right Column: Feature Cards */}
        <div className="relative">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="grid gap-6"
          >
            <GlassCard className="glass-hover" glow>
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-blue-500/20 text-blue-400">
                  <Activity className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Sepsis Prediction</h3>
                  <p className="text-gray-400">Early detection of sepsis risk using advanced machine learning models.</p>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="glass-hover translate-x-8" glow>
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400">
                  <Brain className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Mortality Risk</h3>
                  <p className="text-gray-400">Accurate mortality prediction to assist clinical decision making.</p>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="glass-hover" glow>
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-green-500/20 text-green-400">
                  <Shield className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Secure & Private</h3>
                  <p className="text-gray-400">Enterprise-grade security with role-based access control.</p>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </main>
    </div>
  );
}

