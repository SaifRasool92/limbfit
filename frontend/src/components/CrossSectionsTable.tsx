'use client';

import React from 'react';
import { CrossSection } from '@/types';

interface CrossSectionsTableProps {
  sections: CrossSection[];
}

export function CrossSectionsTable({ sections }: CrossSectionsTableProps) {
  if (!sections || sections.length === 0) {
    return <div className="p-6 text-center text-zinc-500 text-sm">No cross section data available.</div>;
  }

  return (
    <div className="card p-5 space-y-4 max-h-[520px] overflow-y-auto">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-zinc-100 text-sm">Cross-Sectional Slice Analysis</h3>
          <p className="text-zinc-500 text-xs mt-0.5">Anatomical contours reconstructed in millimeters (mm)</p>
        </div>
        <span className="tag font-mono text-xs">{sections.length} Slices</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-400 font-medium">
              <th className="py-2.5 px-3">Slice #</th>
              <th className="py-2.5 px-3">Z Level (mm)</th>
              <th className="py-2.5 px-3">Width (AP mm)</th>
              <th className="py-2.5 px-3">Depth (ML mm)</th>
              <th className="py-2.5 px-3">Est. Circumference (mm)</th>
              <th className="py-2.5 px-3">Eq. Diameter (mm)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
            {sections.map((sec, idx) => {
              // Ramanujan ellipse approximation for circumference
              const a = sec.width_mm / 2;
              const b = sec.depth_mm / 2;
              const h = Math.pow(a - b, 2) / Math.pow(a + b, 2);
              const circ = Math.PI * (a + b) * (1 + (3 * h) / (10 + Math.sqrt(4 - 3 * h)));
              const eqDiam = circ / Math.PI;

              return (
                <tr key={idx} className="hover:bg-zinc-900/50 transition-colors">
                  <td className="py-3 px-3 font-mono text-zinc-500">#{idx + 1}</td>
                  <td className="py-3 px-3 font-mono text-blue-400 font-semibold">{sec.z_mm.toFixed(1)} mm</td>
                  <td className="py-3 px-3 font-mono">{sec.width_mm.toFixed(1)} mm</td>
                  <td className="py-3 px-3 font-mono">{sec.depth_mm.toFixed(1)} mm</td>
                  <td className="py-3 px-3 font-mono font-medium text-emerald-400">{circ.toFixed(1)} mm</td>
                  <td className="py-3 px-3 font-mono text-zinc-400">{eqDiam.toFixed(1)} mm</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
