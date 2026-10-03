'use client';

import React from 'react';
import { Lang, i18n } from '@/i18n';

interface StepIndicatorProps {
  currentStep: number;
  lang: Lang;
}

export function StepIndicator({ currentStep, lang }: StepIndicatorProps) {
  const t = i18n[lang];
  const steps = t.steps;

  return (
    <div className="flex items-center gap-0 w-full max-w-2xl mx-auto mb-8">
      {steps.map((step, i) => (
        <React.Fragment key={i}>
          <div className="flex flex-col items-center gap-1.5 flex-1">
            <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-500
              ${i < currentStep ? 'bg-cyan-500 border-cyan-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.5)]' :
                i === currentStep ? 'bg-transparent border-cyan-400 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]' :
                'bg-transparent border-white/20 text-white/30'}`}>
              {i < currentStep ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              ) : i + 1}
            </div>
            <span className={`text-xs font-medium transition-all ${i <= currentStep ? 'text-cyan-300' : 'text-white/30'}`}>
              {step}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div className={`h-0.5 flex-1 -mt-5 transition-all duration-700 ${i < currentStep ? 'bg-cyan-500' : 'bg-white/10'}`} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
