
import React, { useEffect, useRef, useState } from "react";

export default function GigaAudioSphere() {
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const rafRef = useRef<number | null>(null);

  const [started, setStarted] = useState(false);
  const [energy, setEnergy] = useState(0);
  const [speaking, setSpeaking] = useState(false);
  const [ripples, setRipples] = useState<number[]>([]);
  const [hue, setHue] = useState(280); 

  // 🌊 Start microphone
  const startMic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const ctx = new AudioContext();
      await ctx.resume();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 512;
      const src = ctx.createMediaStreamSource(stream);
      src.connect(analyser);

      audioCtxRef.current = ctx;
      analyserRef.current = analyser;
      setStarted(true);
    } catch (err) {
      console.error("Microphone access error:", err);
    }
  };

  // 🔁 Audio loop
  useEffect(() => {
    if (!started || !analyserRef.current) return;

    const analyser = analyserRef.current;
    const data = new Uint8Array(analyser.frequencyBinCount);

    const loop = () => {
      analyser.getByteFrequencyData(data);

      const avg = data.reduce((a, b) => a + b, 0) / data.length;
      const isSpeaking = avg > 22;
      const e = isSpeaking ? avg / 255 : 0;

      setSpeaking(isSpeaking);
      setEnergy(e);

      // 🌊 spawn ripples
      if (isSpeaking && Math.random() > 0.75) {
        setRipples((r) => [...r, Date.now()]);
      }

      // 🎨 hue cycling
      setHue((h) => (h + 0.8) % 360);

      rafRef.current = requestAnimationFrame(loop);
    };

    loop();
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [started]);

  return (
    <div style={styles.container} onClick={!started ? startMic : undefined}>
      {!started && <div style={styles.tap}></div>}

      {/* Massive Glow Auras */}
      <div
        style={{
          ...styles.glowAura,
          background: `radial-gradient(circle at center,
            hsla(${hue}, 70%, 65%, ${0.35 + energy * 0.15}),
            hsla(${(hue + 40) % 360}, 65%, 55%, ${0.25 + energy * 0.1}),
            hsla(${(hue + 80) % 360}, 60%, 50%, ${0.15 + energy * 0.08}),
            transparent 60%
          )`,
          filter: `blur(${120 + energy * 80}px)`,
        }}
      />

      {/* Secondary Ambient Glow */}
      <div
        style={{
          ...styles.ambientGlow,
          background: `radial-gradient(ellipse at center,
            hsla(${(hue + 180) % 360}, 60%, 50%, ${0.2 + energy * 0.1}),
            hsla(${(hue + 220) % 360}, 55%, 45%, ${0.12 + energy * 0.06}),
            transparent 50%
          )`,
          filter: `blur(${160 + energy * 100}px)`,
        }}
      />

      {/* Ambient Mountain-like Elements */}
      <div style={styles.ambientLeft} />
      <div style={styles.ambientRight} />

      {/* 🌊 Ripples */}
      {ripples.map((id) => (
        <div
          key={id}
          style={{
            ...styles.ripple,
            boxShadow: `rgba(255, 255, 255, 0.1) 0px 0px 0px 1px inset, rgba(0, 0, 0, 0.2) 0px 0px 20px 0px`,
          }}
          onAnimationEnd={() => setRipples((r) => r.filter((x) => x !== id))}
        />
      ))}

      {/* 🔮 Sphere - Giga.ai Style */}
      <div
        style={{
          ...styles.sphere,
          transform: `scale(${1 + energy * 0.1})`,
          boxShadow: `
            rgba(255, 255, 255, 0.15) 0px 0px 0px 1px inset,
            0 0 ${40 + energy * 60}px hsla(${hue}, 70%, 65%, ${0.6 + energy * 0.3}),
            0 0 ${80 + energy * 100}px hsla(${hue}, 65%, 60%, ${0.4 + energy * 0.2})
          `,
        }}
      >
        {/* Video Background */}
        <video
          src="https://framerusercontent.com/assets/CGxYUWS6GTSpiX160RF1KAH7EY.mp4"
          loop
          muted
          playsInline
          autoPlay
          style={styles.video}
        />

        {/* Radial Light Overlay */}
        <div
          style={{
            ...styles.radialLight,
            background: `radial-gradient(65.8333% 65.8333% at 35% 34.1667%, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0) 61.3861%)`,
            opacity: 0.44,
          }}
        />

        {/* Voice Lines Container */}
        <div style={styles.linesContainer}>
          <div style={styles.lines}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  ...styles.line,
                  height: speaking ? 28 + energy * 90 : 16,
                  background: `linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(200, 180, 255, 0.85))`,
                  boxShadow: speaking
                    ? `0 0 ${15 + energy * 30}px rgba(200, 180, 255, 0.8)`
                    : "0 0 5px rgba(200, 180, 255, 0.4)",
                  animation: speaking ? "pulse 0.6s ease-in-out infinite" : "none",
                  animationDelay: `${i * 0.08}s`,
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* 🎨 Styles */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const styles: any = {
  container: {
    height: "80vh",
    background: "linear-gradient(to bottom, #1a1a24 0%, #0f0f18 50%, #1a1820 100%)",
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "flex-end",
    position: "relative",
    overflow: "hidden",
    cursor: "pointer",
    padding: "30px",
  },
  glowAura: {
    position: "absolute",
    bottom: "30px",
    right: "30px",
    width: "800px",
    height: "800px",
    borderRadius: "50%",
    zIndex: 1,
    pointerEvents: "none",
    transition: "all 0.3s ease-out",
  },
  ambientGlow: {
    position: "absolute",
    bottom: "0",
    right: "0",
    width: "700px",
    height: "500px",
    borderRadius: "50%",
    zIndex: 0,
    pointerEvents: "none",
    transition: "all 0.4s ease-out",
  },
  ambientLeft: {
    position: "absolute",
    bottom: 0,
    left: 0,
    width: "40%",
    height: "40%",
    background: "linear-gradient(to top right, rgba(20, 20, 30, 0.8), transparent)",
    filter: "blur(60px)",
    zIndex: 0,
  },
  ambientRight: {
    position: "absolute",
    bottom: 0,
    right: 0,
    width: "40%",
    height: "40%",
    background: "linear-gradient(to top left, rgba(25, 20, 30, 0.8), transparent)",
    filter: "blur(60px)",
    zIndex: 0,
  },
  tap: {
    position: "absolute",
    color: "#fff",
    fontSize: 18,
    fontWeight: 300,
    opacity: 0.7,
    zIndex: 10,
    letterSpacing: "0.5px",
  },
  sphere: {
    width: 230,
    height: 230,
    borderRadius: "1000px",
    position: "relative",
    transition: "transform 0.1s ease-out",
    zIndex: 3,
    overflow: "hidden",
  },
  video: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    borderRadius: "1000px",
    objectFit: "fill",
    objectPosition: "50% 50%",
    display: "block",
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  radialLight: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    pointerEvents: "none",
  },
  linesContainer: {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    zIndex: 5,
  },
  lines: {
    display: "flex",
    gap: 16,
    alignItems: "flex-end",
  },
  line: {
    width: 5,
    borderRadius: 8,
    transition: "height 0.08s ease-out",
  },
  ripple: {
    position: "absolute",
    width: 300,
    height: 300,
    borderRadius: "50%",
    border: "2px solid rgba(200, 150, 255, 0.25)",
    animation: "ripple 1.6s ease-out forwards",
    filter: "blur(2px)",
    zIndex: 2,
  },
};

/* 🔁 Animations */
const style = document.createElement("style");
style.innerHTML = `
@keyframes pulse {
  0%, 100% { 
    transform: scaleY(0.5); 
    opacity: 0.85;
  }
  50% { 
    transform: scaleY(1.8); 
    opacity: 1;
  }
}
@keyframes ripple {
  0% {
    transform: scale(0.95);
    opacity: 0.6;
  }
  100% {
    transform: scale(2.2);
    opacity: 0;
  }
}
`;
document.head.appendChild(style);
