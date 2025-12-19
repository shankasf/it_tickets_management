import React, { useState } from 'react';

const HollywoodGiga: React.FC = () => {
  const [listening, setListening] = useState(false);

  return (
    <div style={styles.appWrapper}>
      {/* 1. CINEMATIC BACKGROUND LAYERS */}
      <div style={styles.mainContent}>
        {/* Dynamic Light Rays / Beams */}
        <div style={{
          ...styles.lightBeams,
          opacity: listening ? 0.4 : 0.1,
        }} />

        {/* High-Visibility Cinematic Mountains */}
        <div style={styles.mountainLayer} />

        {/* Global Atmosphere Glow */}
        <div style={{
          ...styles.atmosphere,
          opacity: listening ? 0.7 : 0.3,
        }} />

        {/* 2. THE HOLLYWOOD SPHERE (Bottom Right) */}
        <div style={styles.spherePosition}>
          <button
            onClick={() => setListening(!listening)}
            style={styles.sphereButton}
          >
            {/* Effect: Cinematic Lens Flare */}
            <div style={{
              ...styles.lensFlare,
              opacity: listening ? 0.8 : 0.2,
              transform: listening ? 'translate(-50%, -50%) scale(1.3)' : 'translate(-50%, -50%) scale(1)',
            }} />

            {/* Effect: Outer Nebula Glow */}
            <div style={styles.nebulaGlow} />

            {/* The Main High-End Sphere */}
            <div style={{
              ...styles.sphereCore,
              animation: 'liquidCycle 12s infinite linear, floating 5s infinite ease-in-out',
            }}>
              {/* Internal 3D Rim & Refractions */}
              <div style={styles.rimLight} />
              <div style={styles.topGloss} />
              
              {/* Dynamic Inner Glow */}
              <div style={styles.innerCoreGlow} />

              {/* Centered Voice Visualizer */}
              <div style={styles.bars}>
                {[0, 1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    style={{
                      ...styles.bar,
                      animation: listening ? `wave 0.5s ${i * 0.1}s infinite` : 'none',
                    }}
                  />
                ))}
              </div>
            </div>
          </button>
        </div>
      </div>

      <style>{animations}</style>
    </div>
  );
};

export default HollywoodGiga;

/* ================= STYLES ================= */

const styles: Record<string, React.CSSProperties> = {
  appWrapper: {
    width: '100vw',
    height: '100vh',
    backgroundColor: '#000',
    overflow: 'hidden',
    position: 'fixed',
    inset: 0,
    margin: 0,
  },
  mainContent: {
    width: '100%',
    height: '100%',
    position: 'relative',
    display: 'flex',
  },
  lightBeams: {
    position: 'absolute',
    inset: 0,
    background: 'repeating-conic-gradient(from 0deg at 85% 85%, transparent 0deg, rgba(255,100,0,0.05) 10deg, transparent 20deg)',
    filter: 'blur(30px)',
    zIndex: 1,
    transition: 'opacity 2s ease',
  },
  mountainLayer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: '100%',
    height: '60vh',
    backgroundImage: 'url("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1920&q=80")',
    backgroundSize: 'cover',
    backgroundPosition: 'bottom center',
    filter: 'brightness(0.6) contrast(1.5) saturate(0.5)',
    zIndex: 2,
  },
  atmosphere: {
    position: 'absolute',
    inset: 0,
    background: 'radial-gradient(circle at 85% 85%, rgba(255, 60, 0, 0.15) 0%, transparent 65%)',
    zIndex: 3,
    transition: 'opacity 1s ease',
  },
  spherePosition: {
    position: 'absolute',
    bottom: '70px',
    right: '100px',
    zIndex: 10,
  },
  sphereButton: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    position: 'relative',
    outline: 'none',
  },
  lensFlare: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    width: '600px',
    height: '600px',
    background: 'radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, rgba(255, 100, 0, 0.05) 40%, transparent 70%)',
    filter: 'blur(40px)',
    zIndex: -1,
    transition: 'transform 0.8s ease, opacity 0.8s ease',
  },
  nebulaGlow: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '400px',
    height: '400px',
    background: 'radial-gradient(circle, rgba(255, 40, 0, 0.3) 0%, transparent 75%)',
    filter: 'blur(60px)',
    zIndex: -1,
  },
  sphereCore: {
    width: '300px',
    height: '300px',
    borderRadius: '50%',
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 50px 100px rgba(0,0,0,0.9), inset 0 0 50px rgba(0,0,0,0.5)',
    overflow: 'hidden',
  },
  rimLight: {
    position: 'absolute',
    inset: 0,
    borderRadius: '50%',
    border: '1.5px solid rgba(255,255,255,0.25)',
    boxShadow: 'inset 10px 10px 30px rgba(255,255,255,0.15), inset -10px -10px 30px rgba(0,0,0,0.8)',
  },
  topGloss: {
    position: 'absolute',
    top: '5%',
    left: '15%',
    width: '50%',
    height: '25%',
    background: 'linear-gradient(to bottom, rgba(255,255,255,0.3), transparent)',
    borderRadius: '50%',
    transform: 'rotate(-15deg)',
    filter: 'blur(1px)',
  },
  innerCoreGlow: {
    position: 'absolute',
    width: '80%',
    height: '80%',
    background: 'radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, transparent 80%)',
    zIndex: 1,
  },
  bars: { display: 'flex', gap: '8px', zIndex: 5 },
  bar: { width: '6px', height: '24px', backgroundColor: '#fff', borderRadius: '4px', boxShadow: '0 0 10px rgba(255,255,255,0.5)' },
};

const animations = `
@keyframes wave {
  0%, 100% { height: 20px; opacity: 0.7; transform: translateY(0); }
  50% { height: 80px; opacity: 1; transform: translateY(-5px); }
}

@keyframes liquidCycle {
  0%   { background: #ff4d00; }
  33%  { background: #ff1f5a; }
  66%  { background: #ff8c00; }
  100% { background: #ff4d00; }
}

@keyframes floating {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-15px) scale(1.02); }
}
`;