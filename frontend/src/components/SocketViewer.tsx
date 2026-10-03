'use client';

import React, { Suspense, useRef, useState, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, ContactShadows, useGLTF, useProgress, Html } from '@react-three/drei';
import * as THREE from 'three';

function Loader() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="flex flex-col items-center gap-2">
        <div className="w-16 h-16 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <span className="text-cyan-300 text-sm font-mono">{progress.toFixed(0)}%</span>
      </div>
    </Html>
  );
}

function SocketModel({ url, showWireframe }: { url: string; showWireframe: boolean }) {
  const { scene } = useGLTF(url);
  const meshRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.003;
    }
  });

  return (
    <group ref={meshRef}>
      <primitive
        object={scene}
        scale={0.01}
      />
      {showWireframe && (
        <primitive
          object={scene.clone()}
          scale={0.0102}
        >
          <meshBasicMaterial wireframe color="#00ffff" opacity={0.3} transparent />
        </primitive>
      )}
    </group>
  );
}

interface SocketViewerProps {
  glbUrl: string;
  showLimb: boolean;
}

export default function SocketViewer({ glbUrl, showLimb }: SocketViewerProps) {
  const [showWireframe, setShowWireframe] = useState(false);
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const fullUrl = `${API_BASE}${glbUrl}`;

  return (
    <div className="relative w-full h-full min-h-[500px] rounded-2xl overflow-hidden border border-white/10">
      {/* Wireframe toggle */}
      <button
        onClick={() => setShowWireframe(v => !v)}
        className="absolute top-4 right-4 z-10 px-3 py-1.5 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20 text-xs text-white hover:bg-white/20 transition-all"
      >
        {showWireframe ? 'Hide Wireframe' : 'Show Wireframe'}
      </button>

      <Canvas
        camera={{ position: [0, 1, 3], fov: 45 }}
        style={{ background: 'transparent' }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 5, 5]} intensity={1.5} castShadow />
        <pointLight position={[-3, 3, -3]} intensity={0.8} color="#00aaff" />

        <Suspense fallback={<Loader />}>
          <SocketModel url={fullUrl} showWireframe={showWireframe} />
          <ContactShadows position={[0, -1.5, 0]} opacity={0.4} scale={5} blur={2} far={4} />
          <Environment preset="city" />
        </Suspense>

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={1}
          maxDistance={10}
        />
      </Canvas>
    </div>
  );
}
