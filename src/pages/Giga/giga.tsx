import React, { useEffect, useRef, useState } from "react";

export default function GigaAudioSphere() {
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const rafRef = useRef<number | null>(null);

  const [started, setStarted] = useState(false);
  const [energy, setEnergy] = useState(0);
  const [speaking, setSpeaking] = useState(false);
  const [ripples, setRipples] = useState<number[]>([]);
  const [hue, setHue] = useState(0);

  
  const startMic = async () => {
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
  };

  
  useEffect(() => {
    if (!started || !analyserRef.current) return;

    const analyser = analyserRef.current;
    const data = new Uint8Array(analyser.frequencyBinCount);

    const loop = () => {
      analyser.getByteFrequencyData(data);

      let sum = 0;
      for (let i = 0; i < data.length; i++) sum += data[i];
      const avg = sum / data.length;

      const isSpeaking = avg > 22; // 🎯 real voice threshold
      const e = isSpeaking ? avg / 255 : 0;

      setSpeaking(isSpeaking);
      setEnergy(e);

    
      if (isSpeaking && Math.random() > 0.75) {
        setRipples((r) => [...r, Date.now()]);
      }

      setHue((h) => (h + 0.8) % 360);

      rafRef.current = requestAnimationFrame(loop);
    };

    loop();

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [started]);

  return (
    // eslint-disable-next-line jsx-a11y/click-events-have-key-events
    <div style={styles.container} onClick={!started ? startMic : undefined}>
      {!started && (
        <div style={styles.tap}>
          Tap to enable microphone
        </div>
      )}

      
      {ripples.map((id) => (
        <div
          key={id}
          style={{
            ...styles.ripple,
            borderColor: `hsl(${hue},100%,60%)`,
          }}
          onAnimationEnd={() =>
            setRipples((r) => r.filter((x) => x !== id))
          }
        />
      ))}

 
      <div
        style={{
          ...styles.sphere,
          background: `radial-gradient(circle at 30% 30%, 
            hsl(${hue},100%,65%), #020202)`,
          transform: `scale(${1 + energy * 0.18})`,
          boxShadow: `
            0 0 ${40 + energy * 120}px hsl(${hue},100%,60%),
            inset 0 0 ${30 + energy * 80}px hsl(${hue},100%,60%)
          `,
        }}
      >
        
        <div style={styles.lines}>
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                ...styles.line,
                height: speaking ? 22 + energy * 80 : 18,
                background: `hsl(${hue},100%,70%)`,
                animation: speaking ? "pulse 0.7s ease-in-out infinite" : "none",
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}


// eslint-disable-next-line @typescript-eslint/no-explicit-any
const styles: any = {
  container: {
    height: "100vh",
    background: "#020202",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
    overflow: "hidden",
    cursor: "pointer",
  },

  tap: {
    position: "absolute",
    color: "#fff",
    fontSize: 18,
    opacity: 0.6,
    zIndex: 10,
  },

  sphere: {
    width: 240,
    height: 240,
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "transform 0.08s linear",
    zIndex: 3,
  },

  lines: {
    display: "flex",
    gap: 14,
    alignItems: "flex-end",
  },

  line: {
    width: 6,
    borderRadius: 6,
    transition: "height 0.1s linear",
  },

  ripple: {
    position: "absolute",
    width: 260,
    height: 260,
    borderRadius: "50%",
    border: "3px solid",
    animation: "ripple 1.4s ease-out forwards",
    filter: "blur(2px)",
    zIndex: 1,
  },
};


const style = document.createElement("style");
style.innerHTML = `
@keyframes pulse {
  0%,100% { transform: scaleY(0.6); }
  50% { transform: scaleY(1.6); }
}

@keyframes ripple {
  from {
    transform: scale(0.8);
    opacity: 0.8;
  }
  to {
    transform: scale(2.2);
    opacity: 0;
  }
}
`;
document.head.appendChild(style);
