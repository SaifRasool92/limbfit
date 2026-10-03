import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'LimbFit AI — Parametric Prosthetic Socket Design',
  description: 'A bilingual web app for rural technicians to photograph a residual limb and receive a 3D-printable transradial socket draft with clinical rationale.',
  keywords: ['prosthetics', 'socket design', '3D printing', 'limb loss', 'Punjab', 'Pakistan', 'AI'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
