"use client";

import { motion } from "framer-motion";
import { ArrowRight, Activity, Brain, Shield, ChevronDown } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { GlassCard } from "@/components/ui/GlassCard";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 relative overflow-hidden">
      {/* Animated background orbs */}
      <motion.div
        animate={{ scale: [1, 1.15, 1] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-blue-500/20 rounded-full blur-[130px] pointer-events-none -z-10"
      />
      <motion.div
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        className="absolute top-0 right-0 w-[400px] h-[400px] bg-purple-500/20 rounded-full blur-[100px] pointer-events-none -z-10"
      />
      <motion.div
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 4 }}
        className="absolute bottom-0 left-0 w-[350px] h-[350px] bg-pink-500/15 rounded-full blur-[100px] pointer-events-none -z-10"
      />

      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        {/* Left */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="space-y-8"
        >
          {/* Status badge */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.06] border border-white/[0.12] backdrop-blur-md"
          >
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500" />
            </span>
            <span className="text-sm font-medium text-gray-300">System Operational</span>
          </motion.div>

          {/* Headline stagger */}
          <div className="space-y-1">
            {[
              { text: "Next-Gen",      cls: "text-white" },
              { text: "Healthcare AI", cls: "text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400" },
              { text: "for ICU",       cls: "text-gray-400" },
            ].map((line, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.12, duration: 0.6, ease: "easeOut" }}
              >
                <span className={`block text-6xl lg:text-7xl font-black tracking-tight ${line.cls}`}>
                  {line.text}
                </span>
              </motion.div>
            ))}
          </div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="text-lg text-gray-300 leading-relaxed max-w-lg"
          >
            Advanced AI-powered diagnostics and mortality prediction system for modern ICUs.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.85 }}
            className="flex flex-wrap gap-4"
          >
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
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="grid grid-cols-3 gap-6 pt-6 border-t border-white/[0.08]"
          >
            {[
              { v: "99%", l: "Accuracy" },
              { v: "24/7", l: "Monitoring" },
              { v: "50+",  l: "Specialists" },
            ].map((s) => (
              <div key={s.l}>
                <p className="text-3xl font-black text-white">{s.v}</p>
                <p className="text-sm text-gray-500 mt-0.5">{s.l}</p>
              </div>
            ))}
          </motion.div>
        </motion.div>

        {/* Right — feature cards */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="grid gap-5"
        >
          {[
            { icon: Activity, title: "Sepsis Prediction",  desc: "Early detection of sepsis risk using advanced ML models.",         grad: "from-red-500 to-orange-500",   shift: "" },
            { icon: Brain,    title: "Mortality Risk",      desc: "Accurate mortality prediction to assist clinical decision making.", grad: "from-purple-500 to-pink-500",   shift: "ml-8" },
            { icon: Shield,   title: "Secure & Private",   desc: "Enterprise-grade security with role-based access control.",        grad: "from-green-500 to-teal-500",    shift: "" },
          ].map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
              className={f.shift}
            >
              <GlassCard glow className="group">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${f.grad} shadow-lg flex-shrink-0 group-hover:scale-110 transition-transform duration-300`}>
                    <f.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-white mb-1">{f.title}</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="absolute bottom-8 flex flex-col items-center gap-1 opacity-30"
      >
        <span className="text-xs text-gray-400">scroll</span>
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </motion.div>
    </div>
  );
}
