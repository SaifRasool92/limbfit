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
      <body className="antialiased">{children}</body>
    </html>
  );
}
