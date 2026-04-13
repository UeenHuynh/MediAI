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
import { useAuthStore } from "@/stores/auth-store";

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

/**
 * Strip a trailing bibliography block from the model answer before display.
 *
 * Removes a block when ALL of the following are true:
 *  1. A line matching a known reference heading exists
 *     (References / Tham khảo / Nguồn tham khảo / Bibliography,
 *      optionally wrapped in ** markdown bold)
 *  2. Every non-blank line after that heading is a [N] numbered entry
 *  3. The block is therefore at the trailing end of the text
 *
 * Does NOT remove [N] markers that appear inside normal prose sentences.
 */
function stripInlineReferences(text: string): string {
    const lines = text.split("\n");

    // Strip markdown bold markers before matching the heading so that
    // "**References:**", "**References**:", and "References:" all match.
    const headingRe =
        /^\s*(?:References|Tham\s+kh[aả]o|Ngu[oồ]n\s+tham\s+kh[aả]o|Bibliography):?\s*$/i;
    const entryRe = /^\s*\*{0,2}\[\d+\]/;

    // Scan backwards for the last reference-heading line
    let headingIdx = -1;
    for (let i = lines.length - 1; i >= 0; i--) {
        if (headingRe.test(lines[i].replace(/\*/g, ""))) {
            headingIdx = i;
            break;
        }
    }

    if (headingIdx === -1) return text;

    // Only strip when everything after the heading is [N] entries or blank lines
    const afterHeading = lines.slice(headingIdx + 1);
    const hasEntries = afterHeading.some((l) => entryRe.test(l));
    const allEntryOrBlank = afterHeading.every(
        (l) => l.trim() === "" || entryRe.test(l)
    );

    if (!hasEntries || !allEntryOrBlank) return text;

    return lines.slice(0, headingIdx).join("\n").trimEnd();
}

/**
 * Strip orphaned [N] citation markers from the answer body when there are no
 * corresponding live sources to display.
 *
 * Called only when getLiveSources() returns an empty array.  In that case every
 * [N] marker in the text is a stub (no real URL / title) so showing it would
 * mislead the reader into thinking there is a citable source.
 *
 * When live sources DO exist we leave the markers in place so the numbered
 * references still correspond to the Sources section below.
 */
function stripOrphanedMarkers(text: string): string {
    return text
        .replace(/\s*\[\d+\]/g, "")   // remove markers and any preceding space
        .replace(/ {2,}/g, " ")        // collapse double-spaces left behind
        .trimEnd();
}

/** Return only sources that have a real public URL and come from a live API tier. */
function getLiveSources(sources: Message["sources"]) {
    if (!sources || sources.length === 0) return [];

    const live = sources.filter(
        (s) =>
            s.sourceType === "live_api" &&
            s.url &&
            s.url.startsWith("http") &&
            !/^Source \d+$/i.test(s.title)
    );

    // Deduplicate: first by URL, then by title
    const seen = new Set<string>();
    return live.filter((s) => {
        const key = s.url || s.title;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
}

export default function ChatbotPage() {
    const router = useRouter();
    const { isAuthenticated } = useAuthStore();
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

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, router]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Show nothing while redirecting
    if (!isAuthenticated) return null;

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
            const is401 = error?.response?.status === 401;
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: is401
                    ? "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."
                    : "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
            if (is401) {
                setTimeout(() => router.push("/login"), 1500);
            }
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
                                    {/* Answer body + Sources share the same liveSources computation */}
                                    {(() => {
                                        const liveSources = getLiveSources(message.sources);

                                        // 1. Strip trailing bibliography block (References: / Tham khảo: …)
                                        // 2. If no live sources exist, also strip orphaned [N] markers from prose
                                        let displayContent = stripInlineReferences(message.content);
                                        if (liveSources.length === 0) {
                                            displayContent = stripOrphanedMarkers(displayContent);
                                        }

                                        return (
                                            <>
                                                <p className="whitespace-pre-wrap">{displayContent}</p>

                                                {/* Sources — live/academic only; hidden when none qualify */}
                                                {liveSources.length > 0 && (
                                                    <div className="mt-3 pt-3 border-t border-white/10">
                                                        <p className="text-xs text-gray-400 mb-2">Sources:</p>
                                                        <div className="space-y-1">
                                                            {liveSources.map((source, idx) => (
                                                                <div key={idx} className="flex items-start gap-2">
                                                                    <span className="inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                                                                        Live Source
                                                                    </span>
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
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </>
                                        );
                                    })()}

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
