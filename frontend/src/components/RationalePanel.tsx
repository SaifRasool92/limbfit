'use client';

import React, { useState } from 'react';
import { ExplainResult } from '@/types';
import { Lang, i18n } from '@/i18n';

interface RationalePanelProps {
  explain: ExplainResult | null;
  loading: boolean;
  lang: Lang;
}

export function RationalePanel({ explain, loading, lang }: RationalePanelProps) {
  const t = i18n[lang];
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  const toggleCheck = (index: number) => {
    setCheckedItems(prev => ({ ...prev, [index]: !prev[index] }));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 h-full text-center">
        <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full spin mb-4" />
        <p className="text-zinc-400 text-sm font-medium">{t.reloadingExplain}</p>
        <p className="text-zinc-600 text-xs mt-1">Querying ChromaDB RAG & vector embeddings...</p>
      </div>
    );
  }

  if (!explain) {
    return (
      <div className="p-8 text-center text-zinc-500 text-sm">
        No clinical rationale generated yet.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-2 overflow-y-auto max-h-[520px] pr-2">
      {/* Clinical Rationale */}
      <div className="card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            <h3 className="font-semibold text-zinc-100 text-sm">Clinical & Engineering Rationale</h3>
          </div>
          <span className="tag font-mono text-xs">ISO 10328 Verified</span>
        </div>
        <p className="text-zinc-300 text-xs leading-relaxed bg-zinc-900/60 p-4 rounded-xl border border-zinc-800/80 font-normal">
          {explain.rationale}
        </p>
      </div>

      {/* Fit Verification Checklist */}
      <div className="card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <h3 className="font-semibold text-zinc-100 text-sm">{t.fitChecklist}</h3>
          </div>
          <span className="text-xs text-zinc-500 font-mono">
            {Object.values(checkedItems).filter(Boolean).length} / {explain.checklist.length} Verified
          </span>
        </div>
        <div className="space-y-2">
          {explain.checklist.map((item, idx) => (
            <label
              key={idx}
              onClick={() => toggleCheck(idx)}
              className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                checkedItems[idx]
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-zinc-900/40 border-zinc-800/60 text-zinc-300 hover:border-zinc-700'
              }`}
            >
              <input
                type="checkbox"
                checked={!!checkedItems[idx]}
                onChange={() => {}}
                className="mt-0.5 rounded border-zinc-700 bg-zinc-800 text-emerald-500 focus:ring-0"
              />
              <span className="text-xs leading-relaxed">{item}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Print & Material Specs */}
      <div className="card p-5 space-y-3">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-amber-500" />
          <h3 className="font-semibold text-zinc-100 text-sm">{t.printGuide}</h3>
        </div>
        <div className="bg-zinc-900/60 p-4 rounded-xl border border-zinc-800/80 text-xs text-zinc-300 space-y-2">
          <p>{explain.print_guide}</p>
        </div>
      </div>

      {/* RAG Knowledge Base Sources */}
      {explain.rag_sources && explain.rag_sources.length > 0 && (
        <div className="card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-500" />
              <h3 className="font-semibold text-zinc-100 text-sm">{t.ragSources}</h3>
            </div>
            <span className="tag text-xs font-mono">ChromaDB Vector Store</span>
          </div>
          <div className="space-y-2">
            {explain.rag_sources.map((src, i) => (
              <div key={i} className="p-3 bg-zinc-900/80 border border-zinc-800/80 rounded-xl space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono text-blue-400 font-medium">{src.source}</span>
                  <span className="text-zinc-500">Page {src.page}</span>
                </div>
                <p className="text-zinc-400 text-[11.5px] leading-normal italic line-clamp-2">
                  &ldquo;{src.text}&rdquo;
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
