'use client';

import React, { useCallback, useState, useRef } from 'react';
import { Lang, i18n } from '@/i18n';

const MAX_SIZE_MB = 20;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/heic'];

interface DropzoneProps {
  label: string;
  id: string;
  onFile: (f: File | null) => void;
  file: File | null;
  lang: Lang;
}

export function ImageDropzone({ label, id, onFile, file, lang }: DropzoneProps) {
  const [drag, setDrag] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = (f: File): string | null => {
    if (!ALLOWED_TYPES.includes(f.type) && !f.name.match(/\.(jpg|jpeg|png|webp|heic)$/i)) {
      return 'Please upload a JPG, PNG, WebP or HEIC image.';
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File is too large (max ${MAX_SIZE_MB} MB).`;
    }
    return null;
  };

  const handleFile = useCallback((f: File) => {
    const err = validate(f);
    if (err) {
      setFileError(err);
      return;
    }
    setFileError(null);
    onFile(f);
  }, [onFile]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const removeFile = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onFile(null);
    setFileError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  const preview = file ? URL.createObjectURL(file) : null;

  return (
    <div className="flex flex-col gap-2">
      <label
        htmlFor={id}
        className={`relative flex flex-col items-center justify-center w-full h-52 rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-300
          ${drag ? 'border-cyan-400 bg-cyan-400/10 scale-105' : 'border-white/20 bg-white/5 hover:border-cyan-400/60 hover:bg-white/10'}
          ${fileError ? 'border-red-500/60' : ''}`}
        onDragOver={e => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        aria-label={label}
      >
        <input
          ref={inputRef}
          id={id}
          type="file"
          accept="image/*"
          capture="environment"
          className="sr-only"
          onChange={handleChange}
          aria-label={label}
        />

        {preview ? (
          <div className="relative w-full h-full">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={preview} alt="preview" className="h-full w-full object-contain rounded-2xl p-2" />
            <button
              onClick={removeFile}
              className="absolute top-2 right-2 w-7 h-7 rounded-full bg-red-500/80 hover:bg-red-500 text-white text-sm flex items-center justify-center transition-all z-10"
              aria-label="Remove image"
            >
              ✕
            </button>
            <div className="absolute bottom-2 left-0 right-0 text-center">
              <span className="text-xs text-white/60 bg-black/40 px-2 py-0.5 rounded-full">
                {file?.name} ({file?.size ? (file.size / 1024).toFixed(0) : 0} KB)
              </span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <svg className="w-11 h-11 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-sm font-semibold text-white/80">{label}</span>
            <span className="text-xs text-white/50">Click or drag & drop · JPG / PNG / WebP</span>
          </div>
        )}
      </label>

      {fileError && (
        <p className="text-xs text-red-400 px-1" role="alert">{fileError}</p>
      )}
    </div>
  );
}
