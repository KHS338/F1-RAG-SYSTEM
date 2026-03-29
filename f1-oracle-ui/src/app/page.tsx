"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [chat, setChat] = useState<{ role: string; text: string; sources?: string[] }[]>([]);
  const [loading, setLoading] = useState(false);

  const askOracle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query;
    setChat((prev) => [...prev, { role: "user", text: userMessage }]);
    setQuery("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage }),
      });

      const data = await response.json();

      setChat((prev) => [
        ...prev,
        { role: "oracle", text: data.answer, sources: data.sources_cited },
      ]);
    } catch (error) {
      setChat((prev) => [
        ...prev,
        { role: "oracle", text: "Communication failure with race control. Check backend." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 p-8 font-sans flex justify-center">
      <div className="max-w-3xl w-full flex flex-col h-[90vh]">
        
        {/* Header */}
        <header className="border-b border-red-600 pb-4 mb-6">
          <h1 className="text-3xl font-bold tracking-tight text-white uppercase flex items-center gap-3">
            <span className="bg-red-600 w-3 h-8 block rounded-sm"></span>
            F1 Regulations Oracle
          </h1>
          <p className="text-neutral-400 mt-2 text-sm">
            Powered by Groq & RAG • Querying the 2026 Sporting Regulations
          </p>
        </header>

        {/* Chat Window */}
        <div className="flex-1 overflow-y-auto pr-4 space-y-6 scrollbar-thin scrollbar-thumb-neutral-800">
          {chat.length === 0 ? (
            <div className="h-full flex items-center justify-center text-neutral-500 italic">
              Awaiting scenario query from pit wall...
            </div>
          ) : (
            chat.map((msg, idx) => (
              <div key={idx} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`max-w-[85%] p-4 rounded-xl ${msg.role === "user" ? "bg-red-700 text-white rounded-br-none" : "bg-neutral-800 text-neutral-200 rounded-bl-none"}`}>
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                  
                  {/* Source Citations */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-neutral-700">
                      <p className="text-xs text-neutral-400 font-semibold mb-2 uppercase">Sources Cited:</p>
                      <ul className="text-xs text-neutral-500 space-y-1 list-disc list-inside">
                        {/* Deduplicate sources before mapping */}
                        {[...new Set(msg.sources)].map((source, sIdx) => (
                          <li key={sIdx}>{source}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="text-neutral-500 animate-pulse text-sm">
              Oracle is scanning regulations...
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={askOracle} className="mt-6 flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What is the penalty for speeding in the pit lane?"
            className="flex-1 bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-all"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </main>
  );
}