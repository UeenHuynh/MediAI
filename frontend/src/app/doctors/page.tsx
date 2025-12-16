"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
    Stethoscope,
    ArrowLeft,
    Search,
    Mail,
    Phone,
    MapPin,
    Grid,
    List,
    User,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import apiClient from "@/lib/api-client";

interface Doctor {
    id: number;
    full_name: string;
    email: string;
    specialty: string;
    department: string;
    phone?: string;
    avatar_url?: string;
}

// Mock data for display purposes
const mockDoctors: Doctor[] = [
    { id: 1, full_name: "Dr. Sarah Chen", email: "sarah.chen@mediai.com", specialty: "Critical Care", department: "ICU", phone: "+1-555-0101" },
    { id: 2, full_name: "Dr. Michael Rodriguez", email: "m.rodriguez@mediai.com", specialty: "Pulmonology", department: "ICU", phone: "+1-555-0102" },
    { id: 3, full_name: "Dr. Emily Watson", email: "e.watson@mediai.com", specialty: "Cardiology", department: "Cardiac ICU", phone: "+1-555-0103" },
    { id: 4, full_name: "Dr. James Kim", email: "j.kim@mediai.com", specialty: "Infectious Disease", department: "ICU", phone: "+1-555-0104" },
    { id: 5, full_name: "Dr. Lisa Thompson", email: "l.thompson@mediai.com", specialty: "Nephrology", department: "ICU", phone: "+1-555-0105" },
];

export default function DoctorsPage() {
    const router = useRouter();
    const [doctors, setDoctors] = useState<Doctor[]>(mockDoctors);
    const [isLoading, setIsLoading] = useState(false);
    const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        const fetchDoctors = async () => {
            setIsLoading(true);
            try {
                const response = await apiClient.get("/doctors");
                if (response.data && response.data.length > 0) {
                    setDoctors(response.data);
                }
            } catch (error) {
                // Use mock data on error
                console.log("Using mock doctor data");
            } finally {
                setIsLoading(false);
            }
        };
        fetchDoctors();
    }, []);

    const filteredDoctors = doctors.filter(
        (doc) =>
            doc.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            doc.specialty.toLowerCase().includes(searchQuery.toLowerCase()) ||
            doc.department.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((n) => n[0])
            .join("")
            .substring(0, 2);
    };

    const getGradient = (id: number) => {
        const gradients = [
            "from-blue-500 to-cyan-500",
            "from-purple-500 to-pink-500",
            "from-green-500 to-emerald-500",
            "from-orange-500 to-red-500",
            "from-indigo-500 to-purple-500",
        ];
        return gradients[id % gradients.length];
    };

    return (
        <div className="min-h-screen p-6">
            {/* Header */}
            <header className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        onClick={() => router.back()}
                        icon={<ArrowLeft className="w-4 h-4" />}
                    >
                        Back
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Doctor Directory</h1>
                        <p className="text-gray-400 mt-1">
                            Browse our team of medical professionals
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* View Toggle */}
                    <div className="flex bg-white/5 rounded-xl p-1">
                        <button
                            onClick={() => setViewMode("grid")}
                            className={`p-2 rounded-lg transition-colors ${viewMode === "grid"
                                    ? "bg-white/10 text-white"
                                    : "text-gray-400 hover:text-white"
                                }`}
                        >
                            <Grid className="w-5 h-5" />
                        </button>
                        <button
                            onClick={() => setViewMode("list")}
                            className={`p-2 rounded-lg transition-colors ${viewMode === "list"
                                    ? "bg-white/10 text-white"
                                    : "text-gray-400 hover:text-white"
                                }`}
                        >
                            <List className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </header>

            {/* Search */}
            <div className="relative mb-8 max-w-md">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                    type="text"
                    placeholder="Search by name, specialty, or department..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
            </div>

            {/* Doctors Grid/List */}
            {viewMode === "grid" ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {filteredDoctors.map((doctor, index) => (
                        <motion.div
                            key={doctor.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                        >
                            <GlassCard className="text-center cursor-pointer hover:border-blue-500/50">
                                {/* Avatar */}
                                <div
                                    className={`w-20 h-20 rounded-full bg-gradient-to-br ${getGradient(
                                        doctor.id
                                    )} flex items-center justify-center mx-auto mb-4 shadow-lg`}
                                >
                                    {doctor.avatar_url ? (
                                        <img
                                            src={doctor.avatar_url}
                                            alt={doctor.full_name}
                                            className="w-full h-full rounded-full object-cover"
                                        />
                                    ) : (
                                        <span className="text-2xl font-bold text-white">
                                            {getInitials(doctor.full_name)}
                                        </span>
                                    )}
                                </div>

                                {/* Info */}
                                <h3 className="text-lg font-semibold text-white">
                                    {doctor.full_name}
                                </h3>
                                <p className="text-blue-400 text-sm">{doctor.specialty}</p>
                                <p className="text-gray-500 text-sm">{doctor.department}</p>

                                {/* Contact */}
                                <div className="mt-4 pt-4 border-t border-white/10 space-y-2">
                                    <a
                                        href={`mailto:${doctor.email}`}
                                        className="flex items-center justify-center gap-2 text-gray-400 hover:text-white text-sm"
                                    >
                                        <Mail className="w-4 h-4" />
                                        {doctor.email}
                                    </a>
                                    {doctor.phone && (
                                        <a
                                            href={`tel:${doctor.phone}`}
                                            className="flex items-center justify-center gap-2 text-gray-400 hover:text-white text-sm"
                                        >
                                            <Phone className="w-4 h-4" />
                                            {doctor.phone}
                                        </a>
                                    )}
                                </div>
                            </GlassCard>
                        </motion.div>
                    ))}
                </div>
            ) : (
                <div className="space-y-4">
                    {filteredDoctors.map((doctor, index) => (
                        <motion.div
                            key={doctor.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                        >
                            <GlassCard className="flex items-center gap-6">
                                {/* Avatar */}
                                <div
                                    className={`w-16 h-16 rounded-full bg-gradient-to-br ${getGradient(
                                        doctor.id
                                    )} flex items-center justify-center flex-shrink-0`}
                                >
                                    <span className="text-xl font-bold text-white">
                                        {getInitials(doctor.full_name)}
                                    </span>
                                </div>

                                {/* Info */}
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-white">
                                        {doctor.full_name}
                                    </h3>
                                    <p className="text-blue-400 text-sm">{doctor.specialty}</p>
                                </div>

                                <div className="text-right">
                                    <p className="text-gray-400 text-sm flex items-center gap-2">
                                        <MapPin className="w-4 h-4" />
                                        {doctor.department}
                                    </p>
                                    <a
                                        href={`mailto:${doctor.email}`}
                                        className="text-blue-400 text-sm hover:underline"
                                    >
                                        {doctor.email}
                                    </a>
                                </div>
                            </GlassCard>
                        </motion.div>
                    ))}
                </div>
            )}

            {/* Empty State */}
            {filteredDoctors.length === 0 && (
                <GlassCard className="flex flex-col items-center justify-center py-16">
                    <User className="w-16 h-16 text-gray-600 mb-4" />
                    <p className="text-gray-400">No doctors found matching your search</p>
                </GlassCard>
            )}
        </div>
    );
}
