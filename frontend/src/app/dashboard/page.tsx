"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
    Activity,
    Heart,
    AlertTriangle,
    Users,
    TrendingUp,
    LogOut,
    Stethoscope,
    Brain,
} from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";

const statsData = [
    {
        title: "Predictions Today",
        value: "142",
        change: "+12%",
        icon: Brain,
        color: "from-blue-500 to-cyan-500",
    },
    {
        title: "High Risk Alerts",
        value: "8",
        change: "-3%",
        icon: AlertTriangle,
        color: "from-red-500 to-pink-500",
    },
    {
        title: "Patients Monitored",
        value: "56",
        change: "+5%",
        icon: Heart,
        color: "from-purple-500 to-violet-500",
    },
    {
        title: "Doctors Active",
        value: "12",
        change: "0%",
        icon: Users,
        color: "from-green-500 to-emerald-500",
    },
];

const quickActions = [
    {
        title: "Sepsis Prediction",
        description: "Assess sepsis risk for ICU patients",
        icon: Activity,
        href: "/predict/sepsis",
        color: "from-red-500 to-orange-500",
    },
    {
        title: "Mortality Prediction",
        description: "Evaluate mortality risk factors",
        icon: TrendingUp,
        href: "/predict/mortality",
        color: "from-purple-500 to-pink-500",
    },
    {
        title: "AI Assistant",
        description: "Ask medical questions with citations",
        icon: Brain,
        href: "/chat",
        color: "from-green-500 to-emerald-500",
    },
    {
        title: "Doctor Directory",
        description: "View doctor profiles and specialties",
        icon: Stethoscope,
        href: "/doctors",
        color: "from-blue-500 to-cyan-500",
    },
];

export default function DashboardPage() {
    const router = useRouter();
    const { user, isAuthenticated, logout } = useAuthStore();

    useEffect(() => {
        if (!isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, router]);

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

    if (!isAuthenticated) {
        return null;
    }

    return (
        <div className="min-h-screen p-6">
            {/* Header */}
            <header className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">Dashboard</h1>
                    <p className="text-gray-400 mt-1">
                        Welcome back, {user?.full_name || user?.username}
                    </p>
                </div>
                <Button variant="ghost" onClick={handleLogout} icon={<LogOut className="w-4 h-4" />}>
                    Logout
                </Button>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {statsData.map((stat, index) => (
                    <motion.div
                        key={stat.title}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <GlassCard className="relative overflow-hidden">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-gray-400 text-sm">{stat.title}</p>
                                    <p className="text-3xl font-bold text-white mt-2">{stat.value}</p>
                                    <p
                                        className={`text-sm mt-1 ${stat.change.startsWith("+")
                                            ? "text-green-400"
                                            : stat.change.startsWith("-")
                                                ? "text-red-400"
                                                : "text-gray-400"
                                            }`}
                                    >
                                        {stat.change} vs yesterday
                                    </p>
                                </div>
                                <div
                                    className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg`}
                                >
                                    <stat.icon className="w-6 h-6 text-white" />
                                </div>
                            </div>
                        </GlassCard>
                    </motion.div>
                ))}
            </div>

            {/* Quick Actions */}
            <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {quickActions.map((action, index) => (
                    <motion.div
                        key={action.title}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 + index * 0.1 }}
                    >
                        <GlassCard
                            className="cursor-pointer group"
                            onClick={() => router.push(action.href)}
                        >
                            <div
                                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                            >
                                <action.icon className="w-6 h-6 text-white" />
                            </div>
                            <h3 className="text-lg font-semibold text-white">{action.title}</h3>
                            <p className="text-gray-400 text-sm mt-1">{action.description}</p>
                        </GlassCard>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
