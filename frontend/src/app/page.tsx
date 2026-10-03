'use client';

import dynamic from 'next/dynamic';
import React, { useState, useCallback, useRef } from 'react';
import { i18n, Lang } from '@/i18n';
import { AnalyzeResult, SocketParams, DEFAULT_PARAMS } from '@/types';
import { ImageDropzone } from '@/components/ImageDropzone';
import { StepIndicator } from '@/components/StepIndicator';
import { ChecksPanel } from '@/components/ChecksPanel';
import { PhotoGuide } from '@/components/PhotoGuide';

const SocketViewer = dynamic(() => import('@/components/SocketViewer'), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [lang, setLang] = useState<Lang>('en');
  const t = i18n[lang];
  const isRTL = lang === 'ur';

  const [step, setStep] = useState(0);
  const [frontFile, setFrontFile] = useState<File | null>(null);
  const [sideFile, setSideFile] = useState<File | null>(null);
  const [markerMm, setMarkerMm] = useState(50);
  const [manualMode, setManualMode] = useState(false);
  const [manualCirc, setManualCirc] = useState('200,210,220,215,200');
  const [manualLength, setManualLength] = useState(250);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [params, setParams] = useState<SocketParams>(DEFAULT_PARAMS);

  const debounceRef = useRef<NodeJS.Timeout>();

  // Can we submit?
  const canAnalyze = manualMode || (frontFile !== null && sideFile !== null);

  const toggleLang = () => setLang(l => l === 'en' ? 'ur' : 'en');

  const handleAnalyze = useCallback(async () => {
    setError(null);
    setLoading(true);
    setStep(1);
    try {
      let res: Response;
      if (manualMode) {
        const circs = manualCirc.split(',').map(Number).filter(n => !isNaN(n));
        if (circs.length < 2) throw new Error('Please enter at least 2 comma-separated circumference values.');
        res = await fetch(`${API}/api/analyze_manual`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ circumferences_mm: circs, length_mm: manualLength }),
        });
      } else {
        if (!frontFile || !sideFile) {
          throw new Error('Please upload both front and side images.');
        }
        const form = new FormData();
        form.append('front_image', frontFile);
        form.append('side_image', sideFile);
        form.append('marker_mm', String(markerMm));
        res = await fetch(`${API}/api/analyze`, { method: 'POST', body: form });
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Server error' }));
        throw new Error(err.detail || 'Server error');
      }

      const data: AnalyzeResult = await res.json();
      setResult(data);
      setStep(3);
    } catch (e: any) {
      setError(e.message);
      setStep(0);
    } finally {
      setLoading(false);
    }
  }, [frontFile, sideFile, markerMm, manualMode, manualCirc, manualLength]);

  const handleParamChange = useCallback((key: keyof SocketParams, value: number) => {
    const newParams = { ...params, [key]: value };
    setParams(newParams);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      if (!result) return;
      try {
        const res = await fetch(`${API}/api/regenerate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sections: result.sections, params: newParams }),
        });
        if (!res.ok) return;
        const data = await res.json();
        setResult(prev => prev ? {
          ...prev,
          socket_glb_url: data.socket_glb_url,
          socket_stl_url: data.socket_stl_url,
          checks: data.checks,
        } : prev);
      } catch (_) {}
    }, 300);
  }, [params, result]);

  const loadDemo = useCallback(() => {
    setManualMode(true);
    setManualCirc('200,220,240,230,215');
    setManualLength(250);
    setStep(0);
    setResult(null);
    setError(null);
  }, []);

  return (
    <div className={`min-h-screen ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>

      {/* Safety Banner */}
      <div className="sticky top-0 z-50 px-4 py-2">
        <div className="safety-banner max-w-4xl mx-auto" role="alert" aria-live="polite">
          {t.safetyBanner}
        </div>
      </div>

      {/* Header */}
      <header className="px-6 py-6 max-w-6xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">
            {t.appName}
          </h1>
          <p className="text-white/60 text-sm mt-0.5">{t.tagline}</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadDemo}
            className="btn-secondary text-sm"
            aria-label="Load demo case with sample measurements"
          >
            {t.loadDemo}
          </button>
          <button
            onClick={toggleLang}
            className="btn-secondary text-sm font-semibold"
            aria-label="Toggle language between English and Urdu"
          >
            {t.language}
          </button>
        </div>
      </header>

      <main className="px-6 pb-16 max-w-6xl mx-auto">
        <StepIndicator currentStep={step} lang={lang} />

        {/* Error */}
        {error && (
          <div
            className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/40 text-red-300 text-sm animate-fade-up"
            role="alert"
            aria-live="assertive"
          >
            ⚠️ {error}
          </div>
        )}

        {/* ─── SCREEN 1: Capture ─── */}
        {!result && (
          <div className="glass p-8 animate-fade-up">
            <h2 className="text-xl font-bold text-white mb-1">{t.captureTitle}</h2>
            {/* Rewording per request item 3 */}
            <p className="text-white/65 text-sm mb-6">
              {lang === 'ur'
                ? 'مارکر کو اعضاء کے پاس رکھیں، کیمرے سے اعضاء جتنے فاصلے پر۔'
                : 'Place the marker beside the limb, the same distance from the camera as the limb.'}
            </p>

            {/* Collapsible photo guide */}
            <PhotoGuide lang={lang} markerSizeMm={markerMm} />

            {/* Manual mode toggle */}
            <label className={`flex items-center gap-3 mb-8 cursor-pointer w-fit ${isRTL ? 'flex-row-reverse' : ''}`}>
              <button
                role="switch"
                aria-checked={manualMode}
                onClick={() => setManualMode(v => !v)}
                className={`w-12 h-6 rounded-full transition-colors ${manualMode ? 'bg-cyan-500' : 'bg-white/15'} relative`}
              >
                <span className={`absolute top-1 w-4 h-4 rounded-full bg-white shadow transition-all ${manualMode ? (isRTL ? 'left-1' : 'left-7') : (isRTL ? 'left-7' : 'left-1')}`} />
              </button>
              <span className="text-white/75 text-sm">{t.manualToggle}</span>
            </label>

            {/* Photo dropzones */}
            {!manualMode ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <ImageDropzone
                  id="front-image-input"
                  label={t.frontView}
                  onFile={setFrontFile}
                  file={frontFile}
                  lang={lang}
                />
                <ImageDropzone
                  id="side-image-input"
                  label={t.sideView}
                  onFile={setSideFile}
                  file={sideFile}
                  lang={lang}
                />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div>
                  <label htmlFor="manual-circs" className="block text-white/75 text-sm font-medium mb-2">
                    {t.circumferences}
                  </label>
                  <input
                    id="manual-circs"
                    type="text"
                    value={manualCirc}
                    onChange={e => setManualCirc(e.target.value)}
                    className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
                    placeholder="e.g. 200,210,220,215,200"
                  />
                </div>
                <div>
                  <label htmlFor="manual-length" className="block text-white/75 text-sm font-medium mb-2">
                    {t.length}
                  </label>
                  <input
                    id="manual-length"
                    type="number"
                    value={manualLength}
                    onChange={e => setManualLength(Number(e.target.value))}
                    min={50}
                    max={500}
                    className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
                  />
                </div>
              </div>
            )}

            {/* Marker size control (photo mode only) */}
            {!manualMode && (
              <div className={`flex items-center gap-4 mb-8 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <label htmlFor="marker-size" className="text-white/75 text-sm font-medium whitespace-nowrap">
                  {t.markerSize}
                </label>
                <input
                  id="marker-size"
                  type="number"
                  value={markerMm}
                  onChange={e => setMarkerMm(Number(e.target.value))}
                  min={20}
                  max={200}
                  className="w-28 bg-white/5 border border-white/15 rounded-xl px-4 py-2 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
            )}

            {/* Analyze button — disabled until ready */}
            <button
              id="analyze-btn"
              onClick={handleAnalyze}
              disabled={loading || !canAnalyze}
              aria-disabled={!canAnalyze}
              title={!canAnalyze ? 'Please upload both front and side photos first.' : ''}
              className={`btn-primary w-full py-4 text-base ${canAnalyze ? 'animate-pulse-glow' : 'opacity-50 cursor-not-allowed shadow-none'}`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-3">
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  {t.analyzing}
                </span>
              ) : t.analyze}
            </button>

            {/* Helper hint when photos missing */}
            {!canAnalyze && !loading && (
              <p className="text-center text-white/45 text-xs mt-3" aria-live="polite">
                {lang === 'ur'
                  ? 'جاری رکھنے کے لیے دونوں تصاویر اپ لوڈ کریں'
                  : 'Upload both photos above to enable analysis'}
              </p>
            )}
          </div>
        )}

        {/* ─── SCREEN 2: Result ─── */}
        {result && (
          <div className="animate-fade-up grid grid-cols-1 xl:grid-cols-3 gap-6">
            {/* 3D Viewer */}
            <div className="xl:col-span-2 glass p-4 h-[560px]">
              <SocketViewer glbUrl={result.socket_glb_url} showLimb={false} />
            </div>

            {/* Right panel */}
            <div className="flex flex-col gap-4">
              {/* Param sliders */}
              <div className="glass p-5">
                <h3 className="font-semibold text-white mb-4 text-sm">{t.socketParams}</h3>
                <div className="space-y-5">
                  {[
                    { key: 'wall_mm' as const, label: t.wallThickness, min: 2, max: 6, step: 0.5 },
                    { key: 'relief_pct' as const, label: t.relief, min: 0, max: 5, step: 0.5 },
                    { key: 'vent_count' as const, label: t.vents, min: 0, max: 12, step: 1 },
                    { key: 'trim_height_mm' as const, label: t.trimHeight, min: 5, max: 30, step: 1 },
                  ].map(({ key, label, min, max, step: stepVal }) => (
                    <div key={key}>
                      <div className={`flex justify-between text-xs text-white/65 mb-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <label htmlFor={`slider-${key}`}>{label}</label>
                        <span className="text-cyan-400 font-mono">{params[key]}</span>
                      </div>
                      <input
                        id={`slider-${key}`}
                        type="range"
                        min={min}
                        max={max}
                        step={stepVal}
                        value={params[key]}
                        onChange={e => handleParamChange(key, Number(e.target.value))}
                        aria-label={label}
                        aria-valuemin={min}
                        aria-valuemax={max}
                        aria-valuenow={params[key]}
                        dir="ltr" // sliders always LTR for usability
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Checks */}
              <div className="glass p-5">
                <h3 className="font-semibold text-white mb-4 text-sm">{t.checks}</h3>
                <ChecksPanel checks={result.checks} lang={lang} />
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-3">
                <a
                  id="download-stl"
                  href={`${API}${result.socket_stl_url}`}
                  download
                  className="btn-primary text-center py-3 text-sm no-underline block"
                  aria-label="Download the 3D printable STL file"
                >
                  ⬇️ {t.downloadSTL}
                </a>
                <button
                  id="back-btn"
                  onClick={() => { setResult(null); setStep(0); }}
                  className="btn-secondary text-sm py-3"
                  aria-label="Go back to capture screen"
                >
                  ← {lang === 'ur' ? 'واپس' : 'Back'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
