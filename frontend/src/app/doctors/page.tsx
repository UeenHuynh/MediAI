"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, Mail, Phone, MapPin, Star, Plus, Grid, List } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { AppShell } from "@/components/ui/AppShell";
import apiClient from "@/lib/api-client";

interface Doctor {
  id: number; full_name: string; email: string;
  specialty: string; department: string; phone?: string; avatar_url?: string;
}

const mockDoctors: Doctor[] = [
  { id: 1, full_name: "Dr. Sarah Chen",        email: "sarah.chen@mediai.com",      specialty: "Critical Care",      department: "ICU",          phone: "+1-555-0101" },
  { id: 2, full_name: "Dr. Michael Rodriguez", email: "m.rodriguez@mediai.com",     specialty: "Pulmonology",        department: "ICU",          phone: "+1-555-0102" },
  { id: 3, full_name: "Dr. Emily Watson",      email: "e.watson@mediai.com",        specialty: "Cardiology",         department: "Cardiac ICU",  phone: "+1-555-0103" },
  { id: 4, full_name: "Dr. James Kim",         email: "j.kim@mediai.com",           specialty: "Infectious Disease", department: "ICU",          phone: "+1-555-0104" },
  { id: 5, full_name: "Dr. Lisa Thompson",     email: "l.thompson@mediai.com",      specialty: "Nephrology",         department: "ICU",          phone: "+1-555-0105" },
];

const GRADIENTS = [
  "from-blue-500 to-cyan-500", "from-purple-500 to-pink-500",
  "from-green-500 to-emerald-500", "from-orange-500 to-red-500", "from-indigo-500 to-purple-500",
];

const getInitials = (name: string) => name.split(" ").map((n) => n[0]).join("").substring(0, 2);

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[]>(mockDoctors);
  const [search, setSearch] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  useEffect(() => {
    apiClient.get("/doctors")
      .then((r) => { if (r.data?.length > 0) setDoctors(r.data); })
      .catch(() => {}); // fallback to mock
  }, []);

  const filtered = doctors.filter((d) =>
    [d.full_name, d.specialty, d.department].some((f) => f.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Doctor Directory</h1>
            <p className="text-sm text-gray-400 mt-0.5">Browse our team of medical professionals</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex bg-white/[0.05] rounded-xl p-1">
              {(["grid", "list"] as const).map((m) => (
                <button key={m} onClick={() => setViewMode(m)}
                  className={`p-2 rounded-lg transition-colors ${viewMode === m ? "bg-white/10 text-white" : "text-gray-400 hover:text-white"}`}>
                  {m === "grid" ? <Grid className="w-4 h-4" /> : <List className="w-4 h-4" />}
                </button>
              ))}
            </div>
            <Button variant="outline" size="sm" icon={<Plus className="w-3.5 h-3.5" />}>Add Doctor</Button>
          </div>
        </div>

        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, specialty, or department..."
            className="w-full pl-10 pr-4 py-2.5 bg-white/[0.06] border border-white/[0.12] rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all" />
        </div>

        {/* Grid */}
        {viewMode === "grid" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((doc, i) => (
              <motion.div key={doc.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
                <GlassCard glow className="text-center group cursor-pointer">
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${GRADIENTS[doc.id % GRADIENTS.length]} flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform`}>
                    {doc.avatar_url
                      ? <img src={doc.avatar_url} alt={doc.full_name} className="w-full h-full rounded-2xl object-cover" />
                      : <span className="text-xl font-bold text-white">{getInitials(doc.full_name)}</span>}
                  </div>
                  <h3 className="font-semibold text-white text-sm">{doc.full_name}</h3>
                  <p className="text-blue-400 text-xs mt-0.5">{doc.specialty}</p>
                  <p className="text-gray-500 text-xs">{doc.department}</p>
                  <div className="mt-4 pt-3 border-t border-white/[0.08] space-y-1.5">
                    <a href={`mailto:${doc.email}`} className="flex items-center justify-center gap-1.5 text-gray-400 hover:text-white text-xs transition-colors">
                      <Mail className="w-3 h-3" />{doc.email}
                    </a>
                    {doc.phone && (
                      <a href={`tel:${doc.phone}`} className="flex items-center justify-center gap-1.5 text-gray-400 hover:text-white text-xs transition-colors">
                        <Phone className="w-3 h-3" />{doc.phone}
                      </a>
                    )}
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((doc, i) => (
              <motion.div key={doc.id} initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
                <GlassCard className="p-4">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${GRADIENTS[doc.id % GRADIENTS.length]} flex items-center justify-center flex-shrink-0`}>
                      <span className="text-sm font-bold text-white">{getInitials(doc.full_name)}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-white text-sm">{doc.full_name}</h3>
                      <p className="text-blue-400 text-xs">{doc.specialty}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-gray-400 text-xs flex items-center gap-1 justify-end"><MapPin className="w-3 h-3" />{doc.department}</p>
                      <a href={`mailto:${doc.email}`} className="text-blue-400 text-xs hover:underline">{doc.email}</a>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        )}

        {filtered.length === 0 && (
          <GlassCard className="flex flex-col items-center justify-center py-16">
            <Search className="w-12 h-12 text-gray-600 mb-3" />
            <p className="text-gray-400 text-sm">No doctors found matching your search</p>
          </GlassCard>
        )}
      </div>
    </AppShell>
  );
}
