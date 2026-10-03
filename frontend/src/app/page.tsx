'use client';

import dynamic from 'next/dynamic';
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { i18n, Lang } from '@/i18n';
import { AnalyzeResult, SocketParams, DEFAULT_PARAMS, ExplainResult } from '@/types';
import { ImageDropzone } from '@/components/ImageDropzone';
import { StepIndicator } from '@/components/StepIndicator';
import { ChecksPanel } from '@/components/ChecksPanel';
import { PhotoGuide } from '@/components/PhotoGuide';
import { RationalePanel } from '@/components/RationalePanel';
import { CrossSectionsTable } from '@/components/CrossSectionsTable';

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

  // Active Tab in Studio View: '3d' | 'rationale' | 'slices'
  const [activeTab, setActiveTab] = useState<'3d' | 'rationale' | 'slices'>('3d');
  const [explainResult, setExplainResult] = useState<ExplainResult | null>(null);
  const [loadingExplain, setLoadingExplain] = useState(false);

  const debounceRef = useRef<NodeJS.Timeout>();

  const canAnalyze = manualMode || (frontFile !== null && sideFile !== null);

  const toggleLang = () => setLang(l => (l === 'en' ? 'ur' : 'en'));

  // Fetch clinical rationale from /api/explain when analysis is done
  const fetchExplanation = useCallback(async (resData: AnalyzeResult, socketParams: SocketParams) => {
    setLoadingExplain(true);
    try {
      const circs = resData.sections.map(s => (s.width_mm + s.depth_mm) * Math.PI / 2);
      const res = await fetch(`${API}/api/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          measurements: { circumferences_mm: circs, total_sections: resData.sections.length },
          params: socketParams,
          checks: resData.checks,
          use_rag: true,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setExplainResult(data);
      }
    } catch (e) {
      console.error('Failed to fetch explanation', e);
    } finally {
      setLoadingExplain(false);
    }
  }, []);

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
      fetchExplanation(data, params);
    } catch (e: any) {
      setError(e.message);
      setStep(0);
    } finally {
      setLoading(false);
    }
  }, [frontFile, sideFile, markerMm, manualMode, manualCirc, manualLength, fetchExplanation, params]);

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
        const updatedResult: AnalyzeResult = {
          ...result,
          socket_glb_url: data.socket_glb_url,
          socket_stl_url: data.socket_stl_url,
          checks: data.checks,
        };
        setResult(updatedResult);
        fetchExplanation(updatedResult, newParams);
      } catch (_) {}
    }, 300);
  }, [params, result, fetchExplanation]);

  const loadDemo = useCallback(() => {
    setManualMode(true);
    setManualCirc('200,220,240,230,215');
    setManualLength(250);
    setStep(0);
    setResult(null);
    setError(null);
  }, []);

  return (
    <div className={`min-h-screen bg-[#080808] text-zinc-100 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 border-b border-zinc-800/80 bg-[#080808]/90 backdrop-blur-md px-6 py-3.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-md shadow-blue-500/20">
              L
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-semibold tracking-tight text-white">{t.appName}</h1>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
                  Studio v1.0
                </span>
              </div>
              <p className="text-xs text-zinc-400 hidden sm:block">{t.tagline}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs text-zinc-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>ChromaDB RAG Active</span>
            </div>

            <button
              onClick={loadDemo}
              className="btn-secondary text-xs"
              aria-label="Load demo case with sample measurements"
            >
              {t.loadDemo}
            </button>

            <button
              onClick={toggleLang}
              className="px-3 py-1.5 rounded-xl border border-zinc-800 bg-zinc-900 hover:border-zinc-700 text-xs font-semibold transition-all text-zinc-300"
              aria-label="Toggle language between English and Urdu"
            >
              {t.language}
            </button>
          </div>
        </div>
      </header>

      {/* Safety Notice Banner */}
      <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-center text-xs text-amber-400 font-medium">
        {t.safetyBanner}
      </div>

      <main className="px-4 md:px-8 py-8 max-w-7xl mx-auto space-y-8">
        {/* Step Indicator */}
        <StepIndicator currentStep={step} lang={lang} />

        {/* Error Alert */}
        {error && (
          <div
            className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs animate-fade-up flex items-center justify-between"
            role="alert"
          >
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)} className="text-zinc-500 hover:text-white text-xs">Dismiss</button>
          </div>
        )}

        {/* ─── SCREEN 1: INPUT & SCAN ─── */}
        {!result && (
          <div className="card p-6 md:p-8 space-y-6 max-w-4xl mx-auto anim-in">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
              <div>
                <h2 className="text-lg font-semibold text-white">{t.captureTitle}</h2>
                <p className="text-zinc-400 text-xs mt-1">{t.captureSubtitle}</p>
              </div>

              {/* Mode Toggle Pills */}
              <div className="flex bg-zinc-900 p-1 rounded-xl border border-zinc-800 w-fit">
                <button
                  onClick={() => setManualMode(false)}
                  className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    !manualMode ? 'bg-blue-600 text-white shadow-sm' : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  📸 Photo Mode (ArUco)
                </button>
                <button
                  onClick={() => setManualMode(true)}
                  className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    manualMode ? 'bg-blue-600 text-white shadow-sm' : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  ✏️ Manual Mode
                </button>
              </div>
            </div>

            {/* Collapsible Photo Guide */}
            {!manualMode && <PhotoGuide lang={lang} markerSizeMm={markerMm} />}

            {/* Photo dropzones */}
            {!manualMode ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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

                {/* Marker size setting */}
                <div className="flex items-center gap-4 bg-zinc-900/60 p-4 rounded-xl border border-zinc-800">
                  <label htmlFor="marker-size" className="text-zinc-300 text-xs font-medium">
                    {t.markerSize}:
                  </label>
                  <input
                    id="marker-size"
                    type="number"
                    value={markerMm}
                    onChange={e => setMarkerMm(Number(e.target.value))}
                    min={20}
                    max={200}
                    className="input w-28 text-xs font-mono"
                  />
                  <span className="text-zinc-500 text-xs">Standard A4 printed ArUco tag = 50.0 mm</span>
                </div>
              </div>
            ) : (
              /* Manual Input Form */
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-zinc-900/40 p-6 rounded-xl border border-zinc-800">
                <div>
                  <label htmlFor="manual-circs" className="block text-zinc-300 text-xs font-medium mb-2">
                    {t.circumferences}
                  </label>
                  <input
                    id="manual-circs"
                    type="text"
                    value={manualCirc}
                    onChange={e => setManualCirc(e.target.value)}
                    className="input font-mono text-xs"
                    placeholder="e.g. 200,210,220,215,200"
                  />
                  <p className="text-zinc-500 text-[11px] mt-1.5">Enter 5 anatomical levels from distal to proximal (mm)</p>
                </div>
                <div>
                  <label htmlFor="manual-length" className="block text-zinc-300 text-xs font-medium mb-2">
                    {t.length}
                  </label>
                  <input
                    id="manual-length"
                    type="number"
                    value={manualLength}
                    onChange={e => setManualLength(Number(e.target.value))}
                    min={50}
                    max={500}
                    className="input font-mono text-xs"
                  />
                  <p className="text-zinc-500 text-[11px] mt-1.5">Total residual limb length (mm)</p>
                </div>
              </div>
            )}

            {/* Analyze Action Button */}
            <div className="pt-2">
              <button
                id="analyze-btn"
                onClick={handleAnalyze}
                disabled={loading || !canAnalyze}
                className={`btn-primary w-full py-3.5 text-sm flex items-center justify-center gap-2 ${
                  canAnalyze ? '' : 'opacity-40 cursor-not-allowed shadow-none'
                }`}
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full spin" />
                    <span>{t.analyzing}</span>
                  </>
                ) : (
                  <>
                    <span>⚡</span>
                    <span>{t.analyze}</span>
                  </>
                )}
              </button>

              {!canAnalyze && !loading && (
                <p className="text-center text-zinc-500 text-xs mt-2.5">
                  {lang === 'ur' ? 'جاری رکھنے کے لیے دونوں تصاویر اپ لوڈ کریں' : 'Please upload both front and side photos to proceed'}
                </p>
              )}
            </div>
          </div>
        )}

        {/* ─── SCREEN 2: STUDIO & PARAMETRIC DESIGN ─── */}
        {result && (
          <div className="anim-in space-y-6">
            {/* Top Bar Actions */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900/60 p-4 rounded-xl border border-zinc-800">
              <div>
                <h2 className="text-base font-semibold text-white">{t.resultTitle}</h2>
                <p className="text-xs text-zinc-400">Parametric Socket Model · Sliced in {result.timings_ms?.geometry ? result.timings_ms.geometry.toFixed(0) : '30'} ms</p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  id="back-btn"
                  onClick={() => {
                    setResult(null);
                    setStep(0);
                  }}
                  className="btn-secondary text-xs"
                >
                  ← {lang === 'ur' ? 'نیا اسکین' : 'New Scan / Input'}
                </button>
                <a
                  id="download-stl"
                  href={`${API}${result.socket_stl_url}`}
                  download
                  className="btn-primary text-xs no-underline inline-flex items-center gap-1.5"
                >
                  <span>⬇️</span>
                  <span>{t.downloadSTL}</span>
                </a>
              </div>
            </div>

            {/* Main Studio Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Interactive Canvas & Tab Panels (2 cols) */}
              <div className="lg:col-span-2 space-y-4">
                <div className="card overflow-hidden">
                  {/* Tabs */}
                  <div className="tab-bar bg-zinc-900/80">
                    <button
                      onClick={() => setActiveTab('3d')}
                      className={`tab ${activeTab === '3d' ? 'active' : ''}`}
                    >
                      🧊 {t.tab3D}
                    </button>
                    <button
                      onClick={() => setActiveTab('rationale')}
                      className={`tab ${activeTab === 'rationale' ? 'active' : ''}`}
                    >
                      📜 {t.tabRationale}
                    </button>
                    <button
                      onClick={() => setActiveTab('slices')}
                      className={`tab ${activeTab === 'slices' ? 'active' : ''}`}
                    >
                      📊 {t.tabSlices}
                    </button>
                  </div>

                  {/* Tab Contents */}
                  <div className="p-4 bg-[#0a0a0b] min-h-[500px]">
                    {activeTab === '3d' && (
                      <div className="w-full h-[520px]">
                        <SocketViewer glbUrl={result.socket_glb_url} showLimb={false} />
                      </div>
                    )}

                    {activeTab === 'rationale' && (
                      <RationalePanel explain={explainResult} loading={loadingExplain} lang={lang} />
                    )}

                    {activeTab === 'slices' && (
                      <CrossSectionsTable sections={result.sections} />
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: Parametric Controls & Quality Gate (1 col) */}
              <div className="space-y-4">
                {/* Parametric Controls Card */}
                <div className="card p-5 space-y-5">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                    <h3 className="font-semibold text-white text-sm">{t.socketParams}</h3>
                    <span className="tag text-xs font-mono">Live Regenerate</span>
                  </div>

                  <div className="space-y-5">
                    {[
                      { key: 'wall_mm' as const, label: t.wallThickness, min: 2.0, max: 6.0, step: 0.5, unit: 'mm' },
                      { key: 'relief_pct' as const, label: t.relief, min: 0.0, max: 5.0, step: 0.5, unit: '%' },
                      { key: 'trim_height_mm' as const, label: t.trimHeight, min: 5, max: 30, step: 1, unit: 'mm' },
                    ].map(({ key, label, min, max, step: stepVal, unit }) => (
                      <div key={key} className="space-y-2">
                        <div className="flex justify-between text-xs text-zinc-300">
                          <label htmlFor={`slider-${key}`}>{label}</label>
                          <span className="mono font-semibold">{params[key]} {unit}</span>
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
                          dir="ltr"
                        />
                      </div>
                    ))}
                  </div>
                </div>

                {/* ISO Quality Gate Card */}
                <div className="card p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                    <h3 className="font-semibold text-white text-sm">{t.checks}</h3>
                    <span className="tag text-xs font-mono">Preliminary</span>
                  </div>
                  <ChecksPanel checks={result.checks} lang={lang} />
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
