"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    MessageSquare,
    ArrowLeft,
    Send,
    Bot,
    User,
    Loader2,
    ExternalLink,
    AlertCircle,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import apiClient from "@/lib/api-client";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    sources?: {
        title: string;
        url: string;
        pmid?: string;
        tier?: string;
        sourceType?: "live_api" | "local" | string;
    }[];
    timestamp: Date;
}

function getSourceBadge(sourceType?: string, tier?: string) {
    if (sourceType === "live_api") {
        let label = "Live API";
        if (tier === "pubmed") label = "Live API: PubMed";
        else if (tier === "scholar") label = "Live API: Scholar";
        return {
            label,
            className: "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
        };
    }

    return {
        label: "Local Knowledge",
        className: "bg-slate-500/15 text-slate-300 border border-slate-500/30",
    };
}

export default function ChatbotPage() {
    const router = useRouter();
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            role: "assistant",
            content:
                "Hello! I'm MediAI Assistant, your medical information helper. I can answer questions about ICU care, sepsis, medical procedures, and provide evidence-based information with citations. How can I help you today?",
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await apiClient.post("/chat", {
                message: userMessage.content,
                include_sources: true,
            });

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: response.data.answer,
                sources: response.data.citations?.map((c: any) => ({
                    title: c.title || c.source,
                    url: c.url || "",
                    pmid: c.pmid,
                    tier: c.tier,
                    sourceType: c.source_type,
                })),
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error: any) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content:
                    "I apologize, but I'm having trouble processing your request. Please try again later.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="min-h-screen flex flex-col p-6">
            {/* Header */}
            <header className="flex items-center gap-4 mb-6">
                <Button
                    variant="ghost"
                    onClick={() => router.back()}
                    icon={<ArrowLeft className="w-4 h-4" />}
                >
                    Back
                </Button>
                <div>
                    <h1 className="text-3xl font-bold text-white">AI Medical Assistant</h1>
                    <p className="text-gray-400 mt-1">
                        Evidence-based medical information with citations
                    </p>
                </div>
            </header>

            {/* Chat Container */}
            <GlassCard className="flex-1 flex flex-col overflow-hidden p-0">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    <AnimatePresence>
                        {messages.map((message) => (
                            <motion.div
                                key={message.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"
                                    }`}
                            >
                                {message.role === "assistant" && (
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                )}
                                <div
                                    className={`max-w-[70%] rounded-2xl p-4 ${message.role === "user"
                                            ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                                            : "bg-white/10 text-gray-100"
                                        }`}
                                >
                                    <p className="whitespace-pre-wrap">{message.content}</p>

                                    {/* Sources */}
                                    {message.sources && message.sources.length > 0 && (
                                        <div className="mt-3 pt-3 border-t border-white/10">
                                            <p className="text-xs text-gray-400 mb-2">Sources:</p>
                                            <div className="space-y-1">
                                                {message.sources.map((source, idx) => (
                                                    <div key={idx} className="flex items-start gap-2">
                                                        <span
                                                            className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium ${getSourceBadge(source.sourceType, source.tier).className}`}
                                                        >
                                                            {getSourceBadge(source.sourceType, source.tier).label}
                                                        </span>
                                                        {source.url ? (
                                                            <a
                                                                href={source.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                                                            >
                                                                <ExternalLink className="w-3 h-3" />
                                                                {source.title}
                                                                {source.pmid && (
                                                                    <span className="text-gray-500">
                                                                        (PMID: {source.pmid})
                                                                    </span>
                                                                )}
                                                            </a>
                                                        ) : (
                                                            <span className="text-xs text-gray-300">
                                                                {source.title}
                                                                {source.pmid && (
                                                                    <span className="text-gray-500">
                                                                        {" "}(PMID: {source.pmid})
                                                                    </span>
                                                                )}
                                                            </span>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <p className="text-xs text-gray-500 mt-2">
                                        {message.timestamp.toLocaleTimeString()}
                                    </p>
                                </div>
                                {message.role === "user" && (
                                    <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                                        <User className="w-5 h-5 text-white" />
                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex gap-3"
                        >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <div className="bg-white/10 rounded-2xl p-4 flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                                <span className="text-gray-400">Thinking...</span>
                            </div>
                        </motion.div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Disclaimer */}
                <div className="px-6 py-2 bg-yellow-500/10 border-t border-yellow-500/20 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                    <span className="text-xs text-yellow-300">
                        This is for informational purposes only. Always consult a healthcare
                        professional for medical advice.
                    </span>
                </div>

                {/* Input */}
                <div className="p-4 border-t border-white/10">
                    <div className="flex gap-3">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask a medical question..."
                            rows={1}
                            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                        />
                        <Button
                            onClick={sendMessage}
                            disabled={!input.trim() || isLoading}
                            icon={<Send className="w-4 h-4" />}
                        >
                            Send
                        </Button>
                    </div>
                </div>
            </GlassCard>
        </div>
    );
}
