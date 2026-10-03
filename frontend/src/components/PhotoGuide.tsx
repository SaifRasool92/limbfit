'use client';

import React, { useState } from 'react';
import { Lang, i18n } from '@/i18n';

interface PhotoGuideProps {
  lang: Lang;
  markerSizeMm: number;
}

const CHECKLIST_EN = [
  { icon: '📍', text: 'Place the printed marker beside the limb at the same distance from the camera as the limb.' },
  { icon: '🔆', text: 'Use good, even lighting — avoid direct sunlight causing harsh shadows.' },
  { icon: '📐', text: 'Keep the phone at limb height and roughly perpendicular — not tilted.' },
  { icon: '🖼️', text: 'Use a plain, single-colour background (white wall, plain fabric) for best segmentation.' },
];

const CHECKLIST_UR = [
  { icon: '📍', text: 'مارکر کو اعضاء کے پاس رکھیں، کیمرے سے اعضاء جتنے فاصلے پر۔' },
  { icon: '🔆', text: 'اچھی، یکساں روشنی استعمال کریں — سایہ بنانے والی دھوپ سے بچیں۔' },
  { icon: '📐', text: 'فون کو اعضاء کی سطح پر اور سیدھا رکھیں۔' },
  { icon: '🖼️', text: 'بہترین نتائج کے لیے سادہ، یکرنگ پس منظر استعمال کریں۔' },
];

export function PhotoGuide({ lang, markerSizeMm }: PhotoGuideProps) {
  const [open, setOpen] = useState(false);
  const t = i18n[lang];
  const isRTL = lang === 'ur';
  const checklist = lang === 'ur' ? CHECKLIST_UR : CHECKLIST_EN;
  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  return (
    <div className="rounded-2xl border border-white/10 overflow-hidden mb-6">
      {/* Collapsible header */}
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-white/5 transition-colors"
        aria-expanded={open}
        aria-controls="photo-guide-content"
      >
        <span className="flex items-center gap-2 text-sm font-semibold text-white/90">
          <span className="text-lg">📷</span>
          {lang === 'ur' ? 'تصویر کیسے لیں؟' : 'How to take the photos'}
        </span>
        <svg
          className={`w-5 h-5 text-white/50 transition-transform duration-300 ${open ? 'rotate-180' : ''}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Collapsible body */}
      {open && (
        <div id="photo-guide-content" className="px-5 pb-5 border-t border-white/10 pt-4 animate-fade-up">
          {/* Checklist */}
          <ul className="space-y-3 mb-5" role="list">
            {checklist.map((item, i) => (
              <li key={i} className={`flex items-start gap-3 text-sm text-white/80 ${isRTL ? 'flex-row-reverse text-right' : ''}`}>
                <span className="text-base mt-0.5 flex-shrink-0" aria-hidden="true">{item.icon}</span>
                <span>{item.text}</span>
              </li>
            ))}
          </ul>

          {/* Good/Bad examples */}
          <div className="grid grid-cols-2 gap-3 mb-5">
            <div className="rounded-xl overflow-hidden border border-green-500/30 bg-green-500/5">
              <div className="bg-green-500/20 text-center text-xs font-semibold text-green-400 py-1.5 flex items-center justify-center gap-1">
                <span>✅</span>
                <span>{lang === 'ur' ? 'درست' : 'Good'}</span>
              </div>
              {/* Inline SVG diagram of good capture */}
              <svg viewBox="0 0 160 120" className="w-full h-28" aria-label="Good photo example">
                <rect width="160" height="120" fill="#0f1a1f" />
                {/* Background wall */}
                <rect x="10" y="20" width="140" height="90" rx="4" fill="#1a2a30" />
                {/* Limb silhouette */}
                <ellipse cx="80" cy="65" rx="22" ry="38" fill="#c8a882" />
                {/* ArUco marker beside it */}
                <rect x="108" y="50" width="20" height="20" fill="white" />
                <rect x="110" y="52" width="16" height="16" fill="black" />
                <rect x="113" y="55" width="10" height="10" fill="white" />
                <rect x="115" y="57" width="3" height="3" fill="black" />
                {/* Label */}
                <text x="80" y="115" textAnchor="middle" fill="#6ee7b7" fontSize="8">Marker beside limb ✓</text>
              </svg>
            </div>

            <div className="rounded-xl overflow-hidden border border-red-500/30 bg-red-500/5">
              <div className="bg-red-500/20 text-center text-xs font-semibold text-red-400 py-1.5 flex items-center justify-center gap-1">
                <span>❌</span>
                <span>{lang === 'ur' ? 'غلط' : 'Bad'}</span>
              </div>
              {/* Inline SVG diagram of bad capture (marker too far, complex bg) */}
              <svg viewBox="0 0 160 120" className="w-full h-28" aria-label="Bad photo example">
                <rect width="160" height="120" fill="#0f1a1f" />
                {/* Cluttered background */}
                <rect x="10" y="20" width="140" height="90" rx="4" fill="#1a2a1a" />
                <rect x="15" y="30" width="30" height="60" fill="#2a4020" opacity="0.7" />
                <rect x="110" y="25" width="35" height="75" fill="#203040" opacity="0.7" />
                {/* Limb tilted */}
                <ellipse cx="75" cy="65" rx="20" ry="35" fill="#c8a882" transform="rotate(15 75 65)" />
                {/* Marker far away / small */}
                <rect x="130" y="90" width="12" height="12" fill="white" opacity="0.6" />
                {/* Label */}
                <text x="80" y="115" textAnchor="middle" fill="#fca5a5" fontSize="8">Cluttered bg, marker far ✗</text>
              </svg>
            </div>
          </div>

          {/* Download marker link */}
          <a
            href={`${API}/api/marker?size_mm=${markerSizeMm}`}
            target="_blank"
            rel="noopener noreferrer"
            download
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-medium hover:bg-cyan-500/20 hover:border-cyan-500/50 transition-all"
            aria-label={`Download printable ArUco marker PDF (${markerSizeMm}mm)`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
            </svg>
            {lang === 'ur'
              ? `قابل پرنٹ ArUco مارکر ڈاؤن لوڈ کریں (${markerSizeMm}mm)`
              : `Download printable ArUco marker PDF (${markerSizeMm}mm)`}
          </a>
        </div>
      )}
    </div>
  );
}
