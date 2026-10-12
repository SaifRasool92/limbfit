import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'LimbFit AI — Parametric Prosthetic Socket Design Studio',
  description: 'A bilingual web application for prosthetists and rural clinics to generate 3D-printable transradial prosthetic sockets with ISO 10328 clinical rationale.',
  keywords: ['prosthetics', 'socket design', '3D printing', 'limb loss', 'Punjab', 'Pakistan', 'AI'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased relative min-h-screen text-zinc-100 overflow-x-hidden">
        {/* Background Video Layer */}
        <div className="fixed inset-0 w-screen h-screen -z-50 overflow-hidden pointer-events-none">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute top-1/2 left-1/2 min-w-full min-h-full w-auto h-auto -translate-x-1/2 -translate-y-1/2 object-cover"
          >
            <source src="/bg.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          {/* Dark Overlay tint for readability */}
          <div className="absolute inset-0 bg-black/60" />
        </div>

        {/* Page Content Layer */}
        <div className="relative z-10 min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}