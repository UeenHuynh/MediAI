"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Save, Key, Trash2, Monitor, Globe, Database, Edit } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { AppShell } from "@/components/ui/AppShell";
import { useAuthStore } from "@/stores/auth-store";

function Toggle({ on, onToggle }: { on: boolean; onToggle: () => void }) {
  return (
    <button onClick={onToggle} title={on ? "Disable" : "Enable"} aria-label={on ? "Disable" : "Enable"}
      className={`w-10 h-5 rounded-full transition-colors duration-300 relative ${on ? "bg-blue-500" : "bg-white/20"}`}>
      <motion.div animate={{ x: on ? 20 : 2 }} transition={{ type: "spring", stiffness: 400, damping: 30 }}
        className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm" />
    </button>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <GlassCard className="p-6">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-5">{title}</h3>
      {children}
    </GlassCard>
  );
}

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [toggles, setToggles] = useState({
    notifications: true,
    emailAlerts: false,
    twoFA: true,
    autoRefresh: true,
    auditLog: true,
  });
  const flip = (k: keyof typeof toggles) => setToggles((p) => ({ ...p, [k]: !p[k] }));
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <AppShell>
      <div className="flex flex-col gap-6 max-w-3xl">
        <div>
          <h1 className="text-2xl font-bold text-white">Settings</h1>
          <p className="text-sm text-gray-400 mt-0.5">Manage your account and system preferences</p>
        </div>

        {/* Profile */}
        <Section title="Account Information">
          <div className="flex items-center gap-5 mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg flex-shrink-0">
              <span className="text-xl font-bold text-white">
                {(user?.full_name ?? user?.username ?? "U").substring(0, 2).toUpperCase()}
              </span>
            </div>
            <div className="flex-1">
              <p className="font-semibold text-white">{user?.full_name || user?.username}</p>
              <p className="text-sm text-gray-400">{user?.email || "—"}</p>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-medium bg-blue-500/15 text-blue-300 border-blue-500/30 mt-1 capitalize">
                {user?.role || "user"}
              </span>
            </div>
            <Button variant="outline" size="sm" icon={<Edit className="w-3 h-3" />}>Edit</Button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Full Name",  value: user?.full_name || "" },
              { label: "Username",   value: user?.username || "" },
              { label: "Email",      value: user?.email || "" },
              { label: "Role",       value: user?.role || "" },
            ].map((f) => (
              <div key={f.label}>
                <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1.5">{f.label}</label>
                <input defaultValue={f.value} placeholder={f.label}
                  className="w-full px-3 py-2.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all" />
              </div>
            ))}
          </div>
        </Section>

        {/* Notifications */}
        <Section title="Notifications">
          <div className="space-y-4">
            {[
              { k: "notifications" as const, label: "Push Notifications",    desc: "Receive alerts for high-risk predictions" },
              { k: "emailAlerts"    as const, label: "Email Alerts",          desc: "Send daily summary reports via email" },
              { k: "autoRefresh"    as const, label: "Auto Refresh Dashboard",desc: "Automatically update data every 30 seconds" },
            ].map((item) => (
              <div key={item.k} className="flex items-center justify-between py-2 border-b border-white/[0.06] last:border-0">
                <div>
                  <p className="text-sm text-white font-medium">{item.label}</p>
                  <p className="text-xs text-gray-500">{item.desc}</p>
                </div>
                <Toggle on={toggles[item.k]} onToggle={() => flip(item.k)} />
              </div>
            ))}
          </div>
        </Section>

        {/* Security */}
        <Section title="Security">
          <div className="space-y-4">
            {[
              { k: "twoFA"     as const, label: "Two-Factor Authentication", desc: "Secure your account with an authenticator app" },
              { k: "auditLog"  as const, label: "HIPAA Audit Log",            desc: "Log all patient data access events" },
            ].map((item) => (
              <div key={item.k} className="flex items-center justify-between py-2 border-b border-white/[0.06] last:border-0">
                <div>
                  <p className="text-sm text-white font-medium">{item.label}</p>
                  <p className="text-xs text-gray-500">{item.desc}</p>
                </div>
                <Toggle on={toggles[item.k]} onToggle={() => flip(item.k)} />
              </div>
            ))}
            <div className="pt-1">
              <Button variant="outline" size="sm" icon={<Key className="w-3 h-3" />}>Change Password</Button>
            </div>
          </div>
        </Section>

        {/* System Info */}
        <Section title="System Information">
          <div className="grid grid-cols-2 gap-3 mb-5">
            {[
              { icon: Monitor,  label: "AI Model",    value: "GPT-4 Turbo / Groq" },
              { icon: Database, label: "Database",    value: "PostgreSQL 15" },
              { icon: Globe,    label: "API Version", value: "v2.4.1" },
              { icon: Database, label: "RAG Index",   value: "12,450 documents" },
            ].map((s) => (
              <div key={s.label} className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.04] border border-white/[0.08]">
                <s.icon className="w-4 h-4 text-gray-500 flex-shrink-0" />
                <div>
                  <p className="text-xs text-gray-500">{s.label}</p>
                  <p className="text-sm font-medium text-white">{s.value}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-3">
            <Button className="flex-1" icon={<Save className="w-4 h-4" />} onClick={handleSave}>
              {saved ? "Saved ✓" : "Save Changes"}
            </Button>
            <Button variant="danger" icon={<Trash2 className="w-4 h-4" />}>Reset</Button>
          </div>
        </Section>
      </div>
    </AppShell>
  );
}
