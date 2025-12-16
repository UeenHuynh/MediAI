"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
    TrendingUp,
    ArrowLeft,
    AlertTriangle,
    CheckCircle,
    User,
    Clock,
    Activity,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import apiClient from "@/lib/api-client";

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
    risk_score: number;
    risk_level: string;
    confidence: number;
    recommendations: string[];
}

export default function MortalityPredictionPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<PredictionResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<MortalityFormData>({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        resolver: zodResolver(mortalitySchema) as any,
        defaultValues: {
            age: 65,
            gender: "M",
            admission_type: "Emergency",
            los_hours: 48,
            sofa_score: 4,
            charlson_index: 2,
            mechanical_ventilation: false,
            vasopressor_use: false,
        },
    });

    const onSubmit = async (data: MortalityFormData) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await apiClient.post("/predict/mortality", data);
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Prediction failed. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case "low": return "from-green-500 to-emerald-500";
            case "medium": return "from-yellow-500 to-orange-500";
            case "high": return "from-orange-500 to-red-500";
            case "critical": return "from-red-500 to-pink-500";
            default: return "from-gray-500 to-gray-600";
        }
    };

    return (
        <div className="min-h-screen p-6">
            {/* Header */}
            <header className="flex items-center gap-4 mb-8">
                <Button variant="ghost" onClick={() => router.back()} icon={<ArrowLeft className="w-4 h-4" />}>
                    Back
                </Button>
                <div>
                    <h1 className="text-3xl font-bold text-white">Mortality Risk Prediction</h1>
                    <p className="text-gray-400 mt-1">Evaluate ICU mortality risk factors</p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Form */}
                <GlassCard>
                    <h2 className="text-xl font-semibold text-white mb-6">Patient Information</h2>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {/* Age & Gender */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">Age</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input
                                        {...register("age")}
                                        type="number"
                                        className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">Gender</label>
                                <select
                                    {...register("gender")}
                                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                >
                                    <option value="M">Male</option>
                                    <option value="F">Female</option>
                                </select>
                            </div>
                        </div>

                        {/* Admission Type */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Admission Type</label>
                            <select
                                {...register("admission_type")}
                                className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                            >
                                <option value="Emergency">Emergency</option>
                                <option value="Elective">Elective</option>
                                <option value="Urgent">Urgent</option>
                            </select>
                        </div>

                        {/* LOS & SOFA */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">Length of Stay (hours)</label>
                                <div className="relative">
                                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input
                                        {...register("los_hours")}
                                        type="number"
                                        className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">SOFA Score (0-24)</label>
                                <div className="relative">
                                    <Activity className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input
                                        {...register("sofa_score")}
                                        type="number"
                                        min="0"
                                        max="24"
                                        className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Charlson Index */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Charlson Comorbidity Index</label>
                            <input
                                {...register("charlson_index")}
                                type="number"
                                className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                            />
                        </div>

                        {/* Checkboxes */}
                        <div className="flex gap-6">
                            <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                                <input {...register("mechanical_ventilation")} type="checkbox" className="w-4 h-4 rounded" />
                                Mechanical Ventilation
                            </label>
                            <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                                <input {...register("vasopressor_use")} type="checkbox" className="w-4 h-4 rounded" />
                                Vasopressor Use
                            </label>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 text-red-400" />
                                <span className="text-red-300 text-sm">{error}</span>
                            </div>
                        )}

                        <Button type="submit" className="w-full" size="lg" loading={isLoading}>
                            Calculate Mortality Risk
                        </Button>
                    </form>
                </GlassCard>

                {/* Result */}
                <div>
                    {result ? (
                        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
                            <GlassCard>
                                <h2 className="text-xl font-semibold text-white mb-6">Prediction Result</h2>
                                <div className="flex flex-col items-center mb-8">
                                    <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${getRiskColor(result.risk_level)} flex items-center justify-center shadow-lg mb-4`}>
                                        <span className="text-4xl font-bold text-white">{Math.round(result.risk_score * 100)}%</span>
                                    </div>
                                    <p className="text-lg font-semibold text-white capitalize">{result.risk_level} Risk</p>
                                    <p className="text-gray-400 text-sm">Confidence: {Math.round(result.confidence * 100)}%</p>
                                </div>
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
                            <TrendingUp className="w-16 h-16 text-gray-600 mb-4" />
                            <p className="text-gray-400 text-center">Enter patient information and click Calculate to see the prediction</p>
                        </GlassCard>
                    )}
                </div>
            </div>
        </div>
    );
}
