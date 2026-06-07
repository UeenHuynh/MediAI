"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Activity, AlertTriangle, CheckCircle, Thermometer, Heart, Wind, Droplets, Zap, BarChart2 } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { AppShell } from "@/components/ui/AppShell";
import apiClient from "@/lib/api-client";

// ─── Schema (unchanged) ───────────────────────────────────────────────────────
const sepsisSchema = z.object({
  age: z.coerce.number().min(0).max(120),
  heart_rate: z.coerce.number().min(0).max(300),
  temperature: z.coerce.number().min(30).max(45),
  respiratory_rate: z.coerce.number().min(0).max(60),
  systolic_bp: z.coerce.number().min(0).max(300),
  diastolic_bp: z.coerce.number().min(0).max(200),
  spo2: z.coerce.number().min(0).max(100),
  wbc: z.coerce.number().min(0).optional(),
  lactate: z.coerce.number().min(0).optional(),
  creatinine: z.coerce.number().min(0).optional(),
});
type SepsisFormData = z.infer<typeof sepsisSchema>;

interface PredictionResult {
  risk_score: number; risk_level: string; confidence: number; recommendations: string[];
}

const getRiskColor = (level: string) => ({
  low: "green", medium: "yellow", high: "red", critical: "red",
}[level] ?? "gray");

const inputFields = [
  { name: "age",              label: "Age",              icon: Activity,   unit: "years",    section: "Patient" },
  { name: "heart_rate",       label: "Heart Rate",       icon: Heart,      unit: "bpm",      section: "Vitals" },
  { name: "temperature",      label: "Temperature",      icon: Thermometer,unit: "°C",       section: "Vitals" },
  { name: "respiratory_rate", label: "Respiratory Rate", icon: Wind,       unit: "/min",     section: "Vitals" },
  { name: "systolic_bp",      label: "Systolic BP",      icon: Droplets,   unit: "mmHg",     section: "Vitals" },
  { name: "diastolic_bp",     label: "Diastolic BP",     icon: Droplets,   unit: "mmHg",     section: "Vitals" },
  { name: "spo2",             label: "SpO₂",             icon: Activity,   unit: "%",        section: "Vitals" },
  { name: "wbc",              label: "WBC Count",        icon: Droplets,   unit: "×10³/µL",  section: "Labs" },
  { name: "lactate",          label: "Lactate",          icon: Droplets,   unit: "mmol/L",   section: "Labs" },
  { name: "creatinine",       label: "Creatinine",       icon: Droplets,   unit: "mg/dL",    section: "Labs" },
];

export default function SepsisPredictionPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<SepsisFormData>({
    resolver: zodResolver(sepsisSchema) as any,
    defaultValues: { age: 65, heart_rate: 88, temperature: 37.5, respiratory_rate: 18, systolic_bp: 120, diastolic_bp: 80, spo2: 96 },
  });

  const onSubmit = async (data: SepsisFormData) => {
    setIsLoading(true); setError(null); setProgress(0); setResult(null);

    // Animate progress bar
    let p = 0;
    const ticker = setInterval(() => { p = Math.min(p + 5, 90); setProgress(p); }, 100);

    try {
      const res = await apiClient.post("/predict/simple/sepsis", {
        age: data.age, heart_rate: data.heart_rate, temperature: data.temperature,
        respiratory_rate: data.respiratory_rate, systolic_bp: data.systolic_bp,
        diastolic_bp: data.diastolic_bp, spo2: data.spo2,
        wbc: data.wbc || null, lactate: data.lactate || null, creatinine: data.creatinine || null,
      });
      clearInterval(ticker); setProgress(100);
      setTimeout(() => {
        setResult({ risk_score: res.data.prediction.risk_score, risk_level: res.data.prediction.risk_level, confidence: res.data.prediction.risk_score, recommendations: [res.data.prediction.recommendation] });
        setIsLoading(false);
      }, 300);
    } catch (err: any) {
      clearInterval(ticker);
      setError(err.response?.data?.detail || "Prediction failed. Please try again.");
      setIsLoading(false);
    }
  };

  const riskPct = result ? Math.round(result.risk_score * 100) : 0;
  const gaugeCirc = 194;

  return (
    <AppShell>
      <div className="flex flex-col gap-5">
        <div>
          <h1 className="text-2xl font-bold text-white">Sepsis Risk Prediction</h1>
          <p className="text-sm text-gray-400 mt-0.5">Enter patient vitals to assess sepsis risk</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Form */}
          <GlassCard className="p-0 overflow-hidden">
            <div className="px-5 py-4 border-b border-white/[0.08]">
              <h2 className="font-semibold text-white text-sm">Patient Vitals</h2>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-5 space-y-5">
              {["Patient", "Vitals", "Labs"].map((section) => {
                const fields = inputFields.filter(f => f.section === section);
                return (
                  <div key={section}>
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                      {section === "Patient" ? "👤 Patient" : section === "Vitals" ? "🫀 Vital Signs" : "🧪 Lab Values"}
                    </p>
                    <div className="grid grid-cols-2 gap-2.5">
                      {fields.map((f) => (
                        <div key={f.name}>
                          <label className="block text-xs text-gray-400 mb-1">{f.label}</label>
                          <div className="relative flex items-center bg-white/[0.05] border border-white/[0.1] rounded-xl overflow-hidden focus-within:border-blue-500/50">
                            <f.icon className="absolute left-2.5 w-3.5 h-3.5 text-gray-500 pointer-events-none" />
                            <input
                              {...register(f.name as keyof SepsisFormData)}
                              type="number" step="any"
                              className="flex-1 pl-8 pr-2 py-2 bg-transparent text-sm text-white focus:outline-none w-0"
                            />
                            <span className="px-2 py-2 text-xs text-gray-500 border-l border-white/[0.08] bg-white/[0.03] whitespace-nowrap">{f.unit}</span>
                          </div>
                          {errors[f.name as keyof SepsisFormData] && <p className="text-[10px] text-red-400 mt-0.5">Invalid value</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}

              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
                  <span className="text-red-300 text-sm">{error}</span>
                </div>
              )}

              {isLoading ? (
                <div className="w-full h-11 rounded-xl bg-white/[0.06] border border-white/[0.1] overflow-hidden relative">
                  <motion.div className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-600 to-purple-600"
                    animate={{ width: `${progress}%` }} transition={{ duration: 0.15 }} />
                  <span className="absolute inset-0 flex items-center justify-center text-sm text-white font-medium">
                    Analyzing... {progress}%
                  </span>
                </div>
              ) : (
                <Button type="submit" className="w-full" size="lg" icon={<Zap className="w-4 h-4" />}>
                  Calculate Risk
                </Button>
              )}
            </form>
          </GlassCard>

          {/* Result */}
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div key="result" initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }} transition={{ type: "spring", stiffness: 180, damping: 22 }}
                className="flex flex-col gap-4">
                <GlassCard glow>
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`w-10 h-10 rounded-xl bg-${getRiskColor(result.risk_level) === "red" ? "red" : getRiskColor(result.risk_level) === "yellow" ? "yellow" : "green"}-500/20 flex items-center justify-center`}>
                      <AlertTriangle className={`w-5 h-5 text-${getRiskColor(result.risk_level) === "red" ? "red" : getRiskColor(result.risk_level) === "yellow" ? "yellow" : "green"}-400`} />
                    </div>
                    <div>
                      <p className="font-semibold text-white text-sm">Prediction Result</p>
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-xs font-medium bg-${getRiskColor(result.risk_level) === "red" ? "red" : getRiskColor(result.risk_level) === "yellow" ? "yellow" : "green"}-500/15 text-${getRiskColor(result.risk_level) === "red" ? "red" : getRiskColor(result.risk_level) === "yellow" ? "yellow" : "green"}-300 border-${getRiskColor(result.risk_level) === "red" ? "red" : getRiskColor(result.risk_level) === "yellow" ? "yellow" : "green"}-500/30`}>
                        {result.risk_level.toUpperCase()} RISK
                      </span>
                    </div>
                  </div>

                  {/* Gauge */}
                  <div className="flex justify-center mb-4">
                    <svg width="160" height="90" viewBox="0 0 160 90">
                      <path d="M18,80 A62,62 0 0,1 142,80" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="13" strokeLinecap="round" />
                      <motion.path d="M18,80 A62,62 0 0,1 142,80" fill="none" stroke="url(#gauge-s)" strokeWidth="13" strokeLinecap="round"
                        strokeDasharray={gaugeCirc} initial={{ strokeDashoffset: gaugeCirc }}
                        animate={{ strokeDashoffset: gaugeCirc * (1 - riskPct / 100) }}
                        transition={{ duration: 1.3, delay: 0.1, ease: "easeOut" }} />
                      <defs><linearGradient id="gauge-s" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#22c55e" /><stop offset="50%" stopColor="#eab308" /><stop offset="100%" stopColor="#ef4444" />
                      </linearGradient></defs>
                      <text x="80" y="70" textAnchor="middle" fill="white" fontSize="24" fontWeight="800">{riskPct}%</text>
                      <text x="80" y="84" textAnchor="middle" fill="#94a3b8" fontSize="8">Sepsis Risk Score</text>
                    </svg>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-center">
                    <div className="bg-white/[0.05] rounded-xl p-3">
                      <p className="text-xl font-bold text-white capitalize">{result.risk_level}</p>
                      <p className="text-xs text-gray-400">Risk Level</p>
                    </div>
                    <div className="bg-white/[0.05] rounded-xl p-3">
                      <p className="text-xl font-bold text-white">{Math.round(result.confidence * 100)}%</p>
                      <p className="text-xs text-gray-400">Confidence</p>
                    </div>
                  </div>
                </GlassCard>

                {result.recommendations?.length > 0 && (
                  <GlassCard className="p-5">
                    <h4 className="text-sm font-semibold text-white mb-3">Recommendations</h4>
                    <ul className="space-y-2">
                      {result.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                          <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />{rec}
                        </li>
                      ))}
                    </ul>
                  </GlassCard>
                )}
              </motion.div>
            ) : (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-white/[0.05] border border-white/[0.1] flex items-center justify-center mx-auto mb-4">
                    <BarChart2 className="w-8 h-8 text-gray-600" />
                  </div>
                  <p className="text-gray-400 text-sm">Enter patient vitals and click<br />"Calculate Risk" to see the prediction</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </AppShell>
  );
}
