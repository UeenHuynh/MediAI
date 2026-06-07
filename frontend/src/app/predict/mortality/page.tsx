"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { TrendingUp, AlertTriangle, CheckCircle, User, Clock, Activity, Zap, BarChart2 } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { AppShell } from "@/components/ui/AppShell";
import apiClient from "@/lib/api-client";

// ─── Schema (unchanged) ───────────────────────────────────────────────────────
const mortalitySchema = z.object({
  age: z.preprocess((a) => Number(a), z.number().min(0).max(120)),
  gender: z.enum(["M", "F"]),
  admission_type: z.string().min(1),
  los_hours: z.preprocess((a) => Number(a), z.number().min(0)),
  sofa_score: z.preprocess((a) => Number(a), z.number().min(0).max(24)),
  charlson_index: z.preprocess((a) => (a ? Number(a) : undefined), z.number().min(0).optional()),
  mechanical_ventilation: z.boolean(),
  vasopressor_use: z.boolean(),
});
type MortalityFormData = z.infer<typeof mortalitySchema>;

interface PredictionResult {
  risk_score: number; risk_level: string; confidence: number; recommendations: string[];
}

export default function MortalityPredictionPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<MortalityFormData>({
    resolver: zodResolver(mortalitySchema) as any,
    defaultValues: { age: 65, gender: "M", admission_type: "Emergency", los_hours: 48, sofa_score: 4, charlson_index: 2, mechanical_ventilation: false, vasopressor_use: false },
  });

  const onSubmit = async (data: MortalityFormData) => {
    setIsLoading(true); setError(null); setProgress(0); setResult(null);
    let p = 0;
    const ticker = setInterval(() => { p = Math.min(p + 5, 90); setProgress(p); }, 100);
    try {
      const res = await apiClient.post("/predict/simple/mortality", {
        age: data.age, gender: data.gender, sofa_score: data.sofa_score,
        los_hours: data.los_hours, mechanical_ventilation: data.mechanical_ventilation,
        vasopressor_use: data.vasopressor_use, charlson_index: data.charlson_index || 0,
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

  const inputCls = "w-full px-4 py-2.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500/50";
  const selectCls = `${inputCls} cursor-pointer`;

  return (
    <AppShell>
      <div className="flex flex-col gap-5">
        <div>
          <h1 className="text-2xl font-bold text-white">Mortality Risk Prediction</h1>
          <p className="text-sm text-gray-400 mt-0.5">Evaluate ICU mortality risk factors</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Form */}
          <GlassCard className="p-0 overflow-hidden">
            <div className="px-5 py-4 border-b border-white/[0.08]">
              <h2 className="font-semibold text-white text-sm">Patient Information</h2>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-5 space-y-4">
              {/* Patient info */}
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">👤 Patient Info</p>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Age</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
                      <input {...register("age")} type="number" className="w-full pl-8 pr-4 py-2.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500/50" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Gender</label>
                    <select {...register("gender")} className={selectCls} style={{ backgroundColor: "rgba(255,255,255,0.05)" }}>
                      <option value="M" style={{ background: "#1e1b4b" }}>Male</option>
                      <option value="F" style={{ background: "#1e1b4b" }}>Female</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Clinical */}
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">🏥 Clinical</p>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Admission Type</label>
                    <select {...register("admission_type")} className={selectCls} style={{ backgroundColor: "rgba(255,255,255,0.05)" }}>
                      <option value="Emergency" style={{ background: "#1e1b4b" }}>Emergency</option>
                      <option value="Elective" style={{ background: "#1e1b4b" }}>Elective</option>
                      <option value="Urgent" style={{ background: "#1e1b4b" }}>Urgent</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">LOS (hours)</label>
                      <div className="relative">
                        <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
                        <input {...register("los_hours")} type="number" className="w-full pl-8 pr-4 py-2.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500/50" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">SOFA Score</label>
                      <div className="relative">
                        <Activity className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
                        <input {...register("sofa_score")} type="number" min="0" max="24" className="w-full pl-8 pr-4 py-2.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500/50" />
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Charlson Comorbidity Index</label>
                    <input {...register("charlson_index")} type="number" className={inputCls} />
                  </div>
                </div>
              </div>

              {/* Flags */}
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">⚕ Interventions</p>
                <div className="flex gap-6">
                  <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input {...register("mechanical_ventilation")} type="checkbox" className="w-4 h-4 rounded accent-blue-500" />
                    Mechanical Ventilation
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input {...register("vasopressor_use")} type="checkbox" className="w-4 h-4 rounded accent-blue-500" />
                    Vasopressor Use
                  </label>
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
                  <span className="text-red-300 text-sm">{error}</span>
                </div>
              )}

              {isLoading ? (
                <div className="w-full h-11 rounded-xl bg-white/[0.06] border border-white/[0.1] overflow-hidden relative">
                  <motion.div className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-600 to-pink-600"
                    animate={{ width: `${progress}%` }} transition={{ duration: 0.15 }} />
                  <span className="absolute inset-0 flex items-center justify-center text-sm text-white font-medium">
                    Analyzing... {progress}%
                  </span>
                </div>
              ) : (
                <Button type="submit" className="w-full" size="lg" icon={<Zap className="w-4 h-4" />}>
                  Calculate Mortality Risk
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
                    <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="font-semibold text-white text-sm">Prediction Result</p>
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-xs font-medium bg-purple-500/15 text-purple-300 border-purple-500/30">
                        {result.risk_level.toUpperCase()} RISK
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-center mb-4">
                    <svg width="160" height="90" viewBox="0 0 160 90">
                      <path d="M18,80 A62,62 0 0,1 142,80" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="13" strokeLinecap="round" />
                      <motion.path d="M18,80 A62,62 0 0,1 142,80" fill="none" stroke="url(#gauge-m)" strokeWidth="13" strokeLinecap="round"
                        strokeDasharray={gaugeCirc} initial={{ strokeDashoffset: gaugeCirc }}
                        animate={{ strokeDashoffset: gaugeCirc * (1 - riskPct / 100) }}
                        transition={{ duration: 1.3, delay: 0.1, ease: "easeOut" }} />
                      <defs><linearGradient id="gauge-m" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#22c55e" /><stop offset="50%" stopColor="#eab308" /><stop offset="100%" stopColor="#ef4444" />
                      </linearGradient></defs>
                      <text x="80" y="70" textAnchor="middle" fill="white" fontSize="24" fontWeight="800">{riskPct}%</text>
                      <text x="80" y="84" textAnchor="middle" fill="#94a3b8" fontSize="8">Mortality Risk Score</text>
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
                  <p className="text-gray-400 text-sm">Enter patient information and click<br />"Calculate" to see the prediction</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </AppShell>
  );
}
