"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity, Brain, MessageSquare, Stethoscope,
  Settings, LayoutDashboard, ChevronLeft, ChevronRight, LogOut,
} from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: "Dashboard",        href: "/dashboard" },
  { icon: Activity,        label: "Sepsis Predict",   href: "/predict/sepsis" },
  { icon: Brain,           label: "Mortality Risk",   href: "/predict/mortality" },
  { icon: MessageSquare,   label: "AI Chat",          href: "/chat" },
  { icon: Stethoscope,     label: "Doctors",          href: "/doctors" },
  { icon: Settings,        label: "Settings",         href: "/settings" },
];

export function Sidebar() {
  const router   = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const [collapsed, setCollapsed] = useState(false);

  // Persist collapsed state
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-collapsed");
    if (stored !== null) setCollapsed(stored === "true");
  }, []);

  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem("sidebar-collapsed", String(next));
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").substring(0, 2).toUpperCase()
    : (user?.username?.substring(0, 2).toUpperCase() ?? "U");

  return (
    <motion.aside
      animate={{ width: collapsed ? 68 : 220 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="relative flex-shrink-0 h-screen flex flex-col bg-white/[0.04] backdrop-blur-2xl border-r border-white/[0.08] overflow-hidden z-20"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/[0.08]">
        <div className="relative flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Activity className="w-5 h-5 text-white" />
          <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-green-400 border-2 border-[#0f172a]" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -6 }} transition={{ duration: 0.15 }}
              className="text-lg font-bold text-white whitespace-nowrap"
            >
              Medi<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">AI</span>
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <button
              key={item.href}
              onClick={() => router.push(item.href)}
              className={[
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 relative group",
                active
                  ? "bg-white/[0.10] text-white"
                  : "text-gray-400 hover:bg-white/[0.06] hover:text-gray-200",
              ].join(" ")}
            >
              {active && (
                <motion.span
                  layoutId="nav-active-bar"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full bg-gradient-to-b from-blue-400 to-purple-400"
                />
              )}
              <item.icon className={`w-5 h-5 flex-shrink-0 ${active ? "text-blue-400" : ""}`} />
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }} transition={{ duration: 0.12 }}
                    className="text-sm font-medium whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          );
        })}
      </nav>

      {/* User + Logout */}
      <div className="px-2 py-3 border-t border-white/[0.08]">
        <div className="flex items-center gap-3 px-2 py-1.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-white">{initials}</span>
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                exit={{ opacity: 0 }} className="flex-1 min-w-0"
              >
                <p className="text-sm font-medium text-white truncate">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-gray-500 truncate capitalize">{user?.role || "user"}</p>
              </motion.div>
            )}
          </AnimatePresence>
          <AnimatePresence>
            {!collapsed && (
              <motion.button
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                onClick={handleLogout}
                className="text-gray-500 hover:text-red-400 transition-colors flex-shrink-0"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </motion.button>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={toggle}
        className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-white/10 border border-white/20 flex items-center justify-center hover:bg-white/20 transition-colors z-10"
      >
        {collapsed
          ? <ChevronRight className="w-3 h-3 text-white" />
          : <ChevronLeft  className="w-3 h-3 text-white" />}
      </button>
    </motion.aside>
  );
}
