"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Activity, Heart, AlertTriangle, Users, TrendingUp, Brain, Stethoscope, Bell, Plus } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { AppShell } from "@/components/ui/AppShell";

// Variants dùng chung — stagger từ parent thay vì mỗi item tự delay
const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, delayChildren: 0.05 } },
};
const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.35, ease: "easeOut" } },
};

const statsData = [
  { title: "Predictions Today", value: "142", change: "+12%", up: true,  icon: Brain,          color: "from-blue-500 to-cyan-500" },
  { title: "High Risk Alerts",  value: "8",   change: "-3%",  up: false, icon: AlertTriangle,  color: "from-red-500 to-pink-500" },
  { title: "Patients Monitored",value: "56",  change: "+5%",  up: true,  icon: Heart,          color: "from-purple-500 to-violet-500" },
  { title: "Doctors Active",    value: "12",  change: "0%",   up: null,  icon: Users,          color: "from-green-500 to-emerald-500" },
];

const quickActions = [
  { title: "Sepsis Prediction",  description: "Assess sepsis risk for ICU patients",  icon: Activity,    href: "/predict/sepsis",    color: "from-red-500 to-orange-500" },
  { title: "Mortality Prediction",description: "Evaluate mortality risk factors",      icon: TrendingUp,  href: "/predict/mortality", color: "from-purple-500 to-pink-500" },
  { title: "AI Assistant",       description: "Ask medical questions with citations",  icon: Brain,       href: "/chat",              color: "from-green-500 to-emerald-500" },
  { title: "Doctor Directory",   description: "View doctor profiles and specialties",  icon: Stethoscope, href: "/doctors",           color: "from-blue-500 to-cyan-500" },
];

// Mini sparkline SVG
function SparkLine({ values, color }: { values: number[]; color: string }) {
  const max = Math.max(...values), min = Math.min(...values);
  const w = 60, h = 24;
  const pts = values.map((v, i) =>
    `${(i / (values.length - 1)) * w},${h - ((v - min) / (max - min || 1)) * h}`
  ).join(" ");
  return (
    <svg width={w} height={h} className="opacity-60">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuthStore();

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-sm text-gray-400 mt-0.5">
              Welcome back, {user?.full_name || user?.username} 👋
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="ghost" icon={<Bell className="w-4 h-4" />}>Alerts</Button>
            <Button variant="outline" icon={<Plus className="w-4 h-4" />}>New Prediction</Button>
          </div>
        </div>

        {/* Stats */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {statsData.map((stat) => (
            <motion.div key={stat.title} variants={itemVariants}>
              <GlassCard className="p-5" glow>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-xs text-gray-400 mb-1">{stat.title}</p>
                    <p className="text-3xl font-bold text-white">{stat.value}</p>
                  </div>
                  <div className={`p-2.5 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg`}>
                    <stat.icon className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-medium ${stat.up === true ? "text-green-400" : stat.up === false ? "text-red-400" : "text-gray-400"}`}>
                    {stat.change} vs yesterday
                  </span>
                  <SparkLine
                    values={[40, 55, 48, 70, 65, 80, parseInt(stat.value) % 100 || 50]}
                    color={stat.up === true ? "#4ade80" : stat.up === false ? "#f87171" : "#94a3b8"}
                  />
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Quick Actions</h2>
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
          >
            {quickActions.map((action) => (
              <motion.div key={action.title} variants={itemVariants}>
                <GlassCard className="cursor-pointer group" glow onClick={() => router.push(action.href)}>
                  <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-lg`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-sm font-semibold text-white">{action.title}</h3>
                  <p className="text-gray-400 text-xs mt-1">{action.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </AppShell>
  );
}
