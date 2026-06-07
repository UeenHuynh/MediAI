"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Loader2, ExternalLink, AlertCircle } from "lucide-react";import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { AppShell } from "@/components/ui/AppShell";
import apiClient from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

// ─── Types ────────────────────────────────────────────────────────────────────
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: { title: string; url: string; pmid?: string; tier?: string; sourceType?: string }[];
  timestamp: Date;
}

// ─── Helpers (unchanged from original) ───────────────────────────────────────
function stripInlineReferences(text: string): string {
  const lines = text.split("\n");
  const headingRe = /^\s*(?:References|Tham\s+kh[aả]o|Ngu[oồ]n\s+tham\s+kh[aả]o|Bibliography):?\s*$/i;
  const entryRe = /^\s*\*{0,2}\[\d+\]/;
  let headingIdx = -1;
  for (let i = lines.length - 1; i >= 0; i--) {
    if (headingRe.test(lines[i].replace(/\*/g, ""))) { headingIdx = i; break; }
  }
  if (headingIdx === -1) return text;
  const afterHeading = lines.slice(headingIdx + 1);
  const hasEntries = afterHeading.some((l) => entryRe.test(l));
  const allEntryOrBlank = afterHeading.every((l) => l.trim() === "" || entryRe.test(l));
  if (!hasEntries || !allEntryOrBlank) return text;
  return lines.slice(0, headingIdx).join("\n").trimEnd();
}

function stripOrphanedMarkers(text: string): string {
  return text.replace(/\s*\[\d+\]/g, "").replace(/ {2,}/g, " ").trimEnd();
}

function getLiveSources(sources: Message["sources"]) {
  if (!sources || sources.length === 0) return [];
  const live = sources.filter((s) => s.url && s.url.startsWith("http") && !/^Source \d+$/i.test(s.title));
  const seen = new Set<string>();
  return live.filter((s) => { const key = s.url || s.title; if (seen.has(key)) return false; seen.add(key); return true; });
}

const SUGGESTIONS = [
  "Early signs of sepsis?",
  "qSOFA criteria explained",
  "Septic shock treatment",
  "ICU mortality risk factors",
];

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function ChatbotPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [messages, setMessages] = useState<Message[]>([{
    id: "welcome", role: "assistant", timestamp: new Date(),
    content: "Hello! I'm MediAI Assistant. I can answer questions about ICU care, sepsis, medical procedures, and provide evidence-based information with citations. How can I help you today?",
  }]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { if (!isAuthenticated) router.push("/login"); }, [isAuthenticated, router]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  if (!isAuthenticated) return null;

  const sendMessage = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || isLoading) return;
    setShowSuggestions(false);

    const userMsg: Message = { id: Date.now().toString(), role: "user", content, timestamp: new Date() };
    setMessages((p) => [...p, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await apiClient.post("/chat", { message: content, include_sources: true }, { timeout: 90000 });
      setMessages((p) => [...p, {
        id: (Date.now() + 1).toString(), role: "assistant", timestamp: new Date(),
        content: res.data.answer,
        sources: res.data.citations?.map((c: any) => ({ title: c.title || c.source, url: c.url || "", pmid: c.pmid, tier: c.tier, sourceType: c.source_type })),
      }]);
    } catch (err: any) {
      const is401 = err?.response?.status === 401;
      setMessages((p) => [...p, {
        id: (Date.now() + 1).toString(), role: "assistant", timestamp: new Date(),
        content: is401 ? "Session expired. Redirecting to login..." : "Sorry, the system encountered an error. Please try again.",
      }]);
      if (is401) setTimeout(() => router.push("/login"), 1500);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

  return (
    <AppShell>
      <div className="flex flex-col gap-4" style={{ height: "calc(100vh - 48px)" }}>
        {/* Page title */}
        <div>
          <h1 className="text-2xl font-bold text-white">AI Medical Assistant</h1>
          <p className="text-sm text-gray-400 mt-0.5">Evidence-based information with citations</p>
        </div>

        <GlassCard className="flex-1 flex flex-col p-0 overflow-hidden">
          {/* Chat header */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/[0.08]">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-white text-sm">MediAI Assistant</p>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                  <span className="text-xs text-green-400">Online · RAG Medical DB</span>
                </div>
              </div>
            </div>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-medium bg-purple-500/15 text-purple-300 border-purple-500/30">
              AI Powered
            </span>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            <AnimatePresence>
              {messages.map((msg) => (
                <div key={msg.id}
                  className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  {msg.role === "assistant" && (
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div className={`max-w-[72%] rounded-2xl px-4 py-3 ${msg.role === "user" ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white" : "bg-white/[0.08] border border-white/[0.1] text-gray-100"}`}>
                    {(() => {
                      const live = getLiveSources(msg.sources);
                      let body = stripInlineReferences(msg.content);
                      if (live.length === 0) body = stripOrphanedMarkers(body);
                      return (
                        <>
                          <p className="whitespace-pre-wrap text-sm leading-relaxed">{body}</p>
                          {live.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-white/10">
                              <p className="text-xs text-gray-400 mb-2">Sources:</p>
                              {live.map((s, idx) => (
                                <div key={idx} className="flex items-start gap-2 mb-1">
                                  <span className="inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 whitespace-nowrap">Live</span>
                                  <a href={s.url} target="_blank" rel="noopener noreferrer"
                                    className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300">
                                    <ExternalLink className="w-3 h-3" />{s.title}
                                    {s.pmid && <span className="text-gray-500">(PMID: {s.pmid})</span>}
                                  </a>
                                </div>
                              ))}
                            </div>
                          )}
                          <p className="text-xs text-gray-500 mt-2">{msg.timestamp.toLocaleTimeString()}</p>
                        </>
                      );
                    })()}
                  </div>
                  {msg.role === "user" && (
                    <div className="w-9 h-9 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <User className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <div className="flex gap-3">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white/10 border border-white/[0.1] rounded-2xl px-4 py-3 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                  <span className="text-gray-400 text-sm">Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestion chips */}
          <AnimatePresence>
            {showSuggestions && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 8 }}
                className="px-5 pb-3 flex flex-wrap gap-2">
                {SUGGESTIONS.map((s, i) => (
                  <motion.button key={s} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                    onClick={() => sendMessage(s)}
                    className="px-3 py-1.5 rounded-full bg-white/[0.07] border border-white/[0.12] text-xs text-gray-300 hover:bg-white/[0.12] hover:text-white transition-all">
                    {s}
                  </motion.button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Disclaimer */}
          <div className="px-5 py-2 bg-yellow-500/[0.07] border-t border-yellow-500/20 flex items-center gap-2">
            <AlertCircle className="w-3.5 h-3.5 text-yellow-500 flex-shrink-0" />
            <span className="text-xs text-yellow-300/80">For informational purposes only. Always consult a healthcare professional.</span>
          </div>

          {/* Input */}
          <div className="p-4 border-t border-white/[0.08]">
            <div className="flex gap-3 items-end">
              <textarea value={input} onChange={(e) => { setInput(e.target.value); if (e.target.value) setShowSuggestions(false); }}
                onKeyDown={handleKey} placeholder="Ask a medical question..." rows={1}
                className="flex-1 px-4 py-3 bg-white/[0.06] border border-white/[0.1] rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 resize-none" />
              <Button onClick={() => sendMessage()} disabled={!input.trim() || isLoading} icon={<Send className="w-4 h-4" />}>
                Send
              </Button>
            </div>
          </div>
        </GlassCard>
      </div>
    </AppShell>
  );
}
