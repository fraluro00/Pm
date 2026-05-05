"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import type { BoardData } from "@/lib/kanban";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type AISidebarProps = {
  isOpen: boolean;
  onClose: () => void;
  onBoardUpdate: (board: BoardData) => void;
};

export const AISidebar = ({ isOpen, onClose, onBoardUpdate }: AISidebarProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMessage: Message = { role: "user", content: text };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_message: text,
          history: messages.map((m) => ({ role: m.role, content: m.content })),
        }),
      });
      const data = await res.json();
      setMessages([...nextMessages, { role: "assistant", content: data.message }]);
      if (data.board_update) {
        onBoardUpdate(data.board_update);
      }
    } catch {
      setMessages([
        ...nextMessages,
        { role: "assistant", content: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed right-0 top-0 z-50 flex h-screen w-[380px] flex-col border-l border-[var(--stroke)] bg-white shadow-[var(--shadow)]">
      <div className="flex items-center justify-between border-b border-[var(--stroke)] px-6 py-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
            Assistant
          </p>
          <h2 className="mt-1 font-display text-lg font-semibold text-[var(--navy-dark)]">
            AI Chat
          </h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-full border border-[var(--stroke)] px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] transition hover:text-[var(--navy-dark)]"
        >
          Close
        </button>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <p className="mt-8 text-center text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            Ask me to create, move, or describe cards.
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                msg.role === "user"
                  ? "bg-[var(--secondary-purple)] text-white"
                  : "border border-[var(--stroke)] bg-[var(--surface)] text-[var(--navy-dark)]"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--gray-text)]">
              Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-[var(--stroke)] p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask or request a change..."
            rows={2}
            disabled={loading}
            className="flex-1 resize-none rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] disabled:opacity-60"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="self-end rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:opacity-60"
          >
            Send
          </button>
        </div>
        <p className="mt-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};
