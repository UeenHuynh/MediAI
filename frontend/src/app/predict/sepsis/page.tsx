"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
    Activity,
    ArrowLeft,
    AlertTriangle,
    CheckCircle,
    Thermometer,
    Heart,
    Wind,
    Droplets,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import apiClient from "@/lib/api-client";

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
    risk_score: number;
    risk_level: string;
    confidence: number;
    recommendations: string[];
}

export default function SepsisPredictionPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<PredictionResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<SepsisFormData>({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        resolver: zodResolver(sepsisSchema) as any,
        defaultValues: {
            age: 65,
            heart_rate: 88,
            temperature: 37.5,
            respiratory_rate: 18,
            systolic_bp: 120,
            diastolic_bp: 80,
            spo2: 96,
        },
    });

    const onSubmit = async (data: SepsisFormData) => {
        setIsLoading(true);
        setError(null);

        try {
            // Use simplified endpoint - backend will handle feature imputation
            const payload = {
                age: data.age,
                heart_rate: data.heart_rate,
                temperature: data.temperature,
                respiratory_rate: data.respiratory_rate,
                systolic_bp: data.systolic_bp,
                diastolic_bp: data.diastolic_bp,
                spo2: data.spo2,
                wbc: data.wbc || null,
                lactate: data.lactate || null,
                creatinine: data.creatinine || null,
            };

            const response = await apiClient.post("/predict/simple/sepsis", payload);
            setResult({
                risk_score: response.data.prediction.risk_score,
                risk_level: response.data.prediction.risk_level,
                confidence: response.data.prediction.risk_score,
                recommendations: [response.data.prediction.recommendation],
            });
        } catch (err: any) {
            setError(err.response?.data?.detail || "Prediction failed. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case "low":
                return "from-green-500 to-emerald-500";
            case "medium":
                return "from-yellow-500 to-orange-500";
            case "high":
                return "from-orange-500 to-red-500";
            case "critical":
                return "from-red-500 to-pink-500";
            default:
                return "from-gray-500 to-gray-600";
        }
    };

    const inputFields = [
        { name: "age", label: "Age", icon: Activity, unit: "years" },
        { name: "heart_rate", label: "Heart Rate", icon: Heart, unit: "bpm" },
        { name: "temperature", label: "Temperature", icon: Thermometer, unit: "°C" },
        { name: "respiratory_rate", label: "Respiratory Rate", icon: Wind, unit: "/min" },
        { name: "systolic_bp", label: "Systolic BP", icon: Droplets, unit: "mmHg" },
        { name: "diastolic_bp", label: "Diastolic BP", icon: Droplets, unit: "mmHg" },
        { name: "spo2", label: "SpO2", icon: Activity, unit: "%" },
        { name: "wbc", label: "WBC Count", icon: Droplets, unit: "×10³/µL" },
        { name: "lactate", label: "Lactate", icon: Droplets, unit: "mmol/L" },
        { name: "creatinine", label: "Creatinine", icon: Droplets, unit: "mg/dL" },
    ];

    return (
        <div className="min-h-screen p-6">
            {/* Header */}
            <header className="flex items-center gap-4 mb-8">
                <Button variant="ghost" onClick={() => router.back()} icon={<ArrowLeft className="w-4 h-4" />}>
                    Back
                </Button>
                <div>
                    <h1 className="text-3xl font-bold text-white">Sepsis Risk Prediction</h1>
                    <p className="text-gray-400 mt-1">Enter patient vitals to assess sepsis risk</p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Form */}
                <GlassCard>
                    <h2 className="text-xl font-semibold text-white mb-6">Patient Vitals</h2>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            {inputFields.map((field) => (
                                <div key={field.name}>
                                    <label className="block text-sm font-medium text-gray-300 mb-1">
                                        {field.label}
                                    </label>
                                    <div className="relative">
                                        <field.icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                        <input
                                            {...register(field.name as keyof SepsisFormData)}
                                            type="number"
                                            step="any"
                                            className="w-full pl-10 pr-12 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                        />
                                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500">
                                            {field.unit}
                                        </span>
                                    </div>
                                    {errors[field.name as keyof SepsisFormData] && (
                                        <p className="mt-1 text-xs text-red-400">Invalid value</p>
                                    )}
                                </div>
                            ))}
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 text-red-400" />
                                <span className="text-red-300 text-sm">{error}</span>
                            </div>
                        )}

                        <Button type="submit" className="w-full" size="lg" loading={isLoading}>
                            Calculate Risk
                        </Button>
                    </form>
                </GlassCard>

                {/* Result */}
                <div>
                    {result ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <GlassCard>
                                <h2 className="text-xl font-semibold text-white mb-6">Prediction Result</h2>

                                {/* Risk Score Gauge */}
                                <div className="flex flex-col items-center mb-8">
                                    <div
                                        className={`w-32 h-32 rounded-full bg-gradient-to-br ${getRiskColor(
                                            result.risk_level
                                        )} flex items-center justify-center shadow-lg mb-4`}
                                    >
                                        <span className="text-4xl font-bold text-white">
                                            {Math.round(result.risk_score * 100)}%
                                        </span>
                                    </div>
                                    <p className="text-lg font-semibold text-white capitalize">
                                        {result.risk_level} Risk
                                    </p>
                                    <p className="text-gray-400 text-sm">
                                        Confidence: {Math.round(result.confidence * 100)}%
                                    </p>
                                </div>

                                {/* Recommendations */}
                                {result.recommendations?.length > 0 && (
                                    <div>
                                        <h3 className="text-lg font-medium text-white mb-3">Recommendations</h3>
                                        <ul className="space-y-2">
                                            {result.recommendations.map((rec, idx) => (
                                                <li key={idx} className="flex items-start gap-2 text-gray-300">
                                                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                                                    <span>{rec}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </GlassCard>
                        </motion.div>
                    ) : (
                        <GlassCard className="flex flex-col items-center justify-center h-full min-h-[400px]">
                            <Activity className="w-16 h-16 text-gray-600 mb-4" />
                            <p className="text-gray-400 text-center">
                                Enter patient vitals and click Calculate Risk to see the prediction
                            </p>
                        </GlassCard>
                    )}
                </div>
            </div>
        </div>
    );
}
