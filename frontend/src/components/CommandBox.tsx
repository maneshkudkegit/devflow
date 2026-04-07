/**
 * DevFlow – CommandBox component.
 * A terminal‑style input that sends free‑text DevOps commands
 * to the backend and displays the result inline.
 */

import { useState, useRef, useEffect } from 'react';
import { Terminal, Send, Loader2, CheckCircle2, XCircle, Info } from 'lucide-react';
import { runCommand, type CommandResult } from '../services/api';

interface HistoryEntry {
  command: string;
  result: CommandResult | null;
  error: string | null;
  timestamp: Date;
}

export default function CommandBox() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    '/devflow help',
    '/devflow create_user username=john role=PUBLIC',
    '/devflow reset_password username=john',
    '/devflow list_users',
    'deploy backend',
  ];

  useEffect(() => {
    historyRef.current?.scrollTo({ top: historyRef.current.scrollHeight, behavior: 'smooth' });
  }, [history]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cmd = input.trim();
    if (!cmd || loading) return;

    setLoading(true);
    setInput('');

    try {
      const result = await runCommand(cmd);
      setHistory((h) => [...h, { command: cmd, result, error: null, timestamp: new Date() }]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setHistory((h) => [...h, { command: cmd, result: null, error: msg, timestamp: new Date() }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="glass-card overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-3 border-b border-glass-border bg-surface-100/40">
        <div className="flex gap-1.5">
          <span className="w-3 h-3 rounded-full bg-red-500/80" />
          <span className="w-3 h-3 rounded-full bg-amber-500/80" />
          <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
        </div>
        <div className="flex items-center gap-2 text-gray-400">
          <Terminal className="w-4 h-4" />
          <span className="text-xs font-medium">DevFlow Terminal</span>
        </div>
      </div>

      {/* History */}
      <div ref={historyRef} className="max-h-64 overflow-y-auto p-4 space-y-3 font-mono text-sm">
        {history.length === 0 && (
          <div className="space-y-3">
            <p className="text-gray-600 text-xs select-none">
              Start with <code className="text-df-400">/devflow help</code> to see commands and examples.
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((cmd) => (
                <button
                  key={cmd}
                  type="button"
                  onClick={() => setInput(cmd)}
                  className="rounded-full border border-df-500/20 bg-df-700/40 px-3 py-1 text-[11px] text-gray-300 hover:border-df-400 hover:bg-df-600 transition"
                >
                  {cmd}
                </button>
              ))}
            </div>
          </div>
        )}
        {history.map((entry, i) => (
          <div key={i} className="animate-slide-up">
            <div className="flex items-center gap-2 text-df-400">
              <span className="text-df-600">$</span>
              <span>{entry.command}</span>
            </div>
            {entry.result && (
              <div
                className={`mt-1 ml-4 flex items-start gap-2 text-xs ${
                  entry.result.status === 'success' ? 'text-emerald-400' : 'text-red-400'
                }`}
              >
                {entry.result.status === 'success' ? (
                  <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                ) : (
                  <XCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                )}
                <span>{entry.result.message || JSON.stringify(entry.result)}</span>
              </div>
            )}
            {entry.error && (
              <div className="mt-1 ml-4 flex items-start gap-2 text-xs text-red-400">
                <XCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                <span>{entry.error}</span>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-df-400 animate-pulse">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span className="text-xs">Processing…</span>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2 px-4 py-3 border-t border-glass-border">
        <span className="text-df-500 font-mono text-sm font-bold">$</span>
        <input
          id="commandbox-input"
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type /devflow help or deploy backend..."
          className="flex-1 bg-transparent text-sm text-gray-200 placeholder-gray-600 outline-none font-mono"
          disabled={loading}
          autoComplete="off"
          spellCheck={false}
        />
        <button
          type="button"
          onClick={() => setInput('/devflow help')}
          className="px-3 py-2 rounded-lg text-df-400 hover:text-white hover:bg-df-500/20 transition-all"
        >
          <Info className="w-4 h-4" />
        </button>
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-2 rounded-lg text-df-400 hover:text-df-300 hover:bg-df-500/10 transition-all disabled:opacity-30"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>
    </div>
  );
}
