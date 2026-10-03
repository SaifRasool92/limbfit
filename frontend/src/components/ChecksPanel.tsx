'use client';

import React from 'react';
import { Checks } from '@/types';
import { Lang, i18n } from '@/i18n';

interface ChecksPanelProps {
  checks: Checks;
  lang: Lang;
}

export function ChecksPanel({ checks, lang }: ChecksPanelProps) {
  const t = i18n[lang];

  const items = [
    {
      label: t.watertight,
      value: checks.is_watertight ? t.yes : t.no,
      ok: checks.is_watertight,
      icon: '🔒',
    },
    {
      label: t.weight,
      value: `${checks.weight_grams} ${t.grams}`,
      ok: checks.weight_grams < 200,
      icon: '⚖️',
    },
    {
      label: t.cost,
      value: `Rs ${checks.cost_estimate.toFixed(0)}`,
      ok: true,
      icon: '💰',
    },
    {
      label: t.overhang,
      value: `${checks.max_overhang_deg}${t.degrees}`,
      ok: checks.max_overhang_deg < 45,
      icon: '📐',
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {items.map((item, i) => (
        <div
          key={i}
          className={`rounded-xl p-3 border transition-all
            ${item.ok
              ? 'border-green-500/30 bg-green-500/10'
              : 'border-red-500/30 bg-red-500/10'}`}
        >
          <div className="flex items-center gap-2 mb-1">
            <span>{item.icon}</span>
            <span className="text-xs text-white/60">{item.label}</span>
          </div>
          <div className={`text-sm font-bold ${item.ok ? 'text-green-400' : 'text-red-400'}`}>
            {item.value}
          </div>
        </div>
      ))}
    </div>
  );
}
