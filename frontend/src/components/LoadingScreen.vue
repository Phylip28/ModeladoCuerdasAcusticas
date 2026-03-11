<template>
  <div class="loading-screen" aria-label="Cargando aplicación">
    <!-- Oscilloscope screen -->
    <div class="osc-frame">
      <!-- CRT scanline overlay -->
      <div class="crt-overlay" />

      <!-- Grid -->
      <svg
        class="osc-grid"
        viewBox="0 0 600 180"
        preserveAspectRatio="xMidYMid slice"
      >
        <!-- Horizontal grid lines (5 divisions) -->
        <line
          v-for="y in [36, 72, 108, 144]"
          :key="'h' + y"
          :x1="0"
          :y1="y"
          x2="600"
          :y2="y"
          stroke="rgba(0,212,170,0.08)"
          stroke-width="1"
        />
        <!-- Vertical grid lines (5 divisions) -->
        <line
          v-for="x in [120, 240, 360, 480]"
          :key="'v' + x"
          :x1="x"
          y1="0"
          :x2="x"
          y2="180"
          stroke="rgba(0,212,170,0.08)"
          stroke-width="1"
        />
        <!-- Center axes -->
        <line
          x1="0"
          y1="90"
          x2="600"
          y2="90"
          stroke="rgba(0,212,170,0.15)"
          stroke-width="1"
        />
        <line
          x1="300"
          y1="0"
          x2="300"
          y2="180"
          stroke="rgba(0,212,170,0.15)"
          stroke-width="1"
        />
      </svg>

      <!-- Wave canvas (clips at 600×180) -->
      <div class="wave-clip">
        <svg
          class="wave-svg"
          viewBox="0 0 600 180"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="none"
        >
          <defs>
            <filter id="ls-glow" x="-20%" y="-80%" width="140%" height="260%">
              <feGaussianBlur
                in="SourceGraphic"
                stdDeviation="3.5"
                result="blur"
              />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <!-- Ghost trace (phase-shifted +150px) -->
          <g class="wave-ghost-g">
            <!-- 4 periods = 1200px wide so the 300px period loops seamlessly -->
            <path
              class="wave-ghost"
              d="M-150 90
                 C-67.1 50,-82.9 50,0 90
                 S67.1 130,150 90
                 S217.1 50,300 90
                 S367.1 130,450 90
                 S517.1 50,600 90
                 S667.1 130,750 90
                 S817.1 50,900 90
                 S967.1 130,1050 90"
            />
          </g>

          <!-- Main bright trace -->
          <g class="wave-main-g" filter="url(#ls-glow)">
            <path
              class="wave-main"
              d="M0 90
                 C82.9 50,67.1 50,150 90
                 S217.1 130,300 90
                 S367.1 50,450 90
                 S517.1 130,600 90
                 S667.1 50,750 90
                 S817.1 130,900 90
                 S967.1 50,1050 90
                 S1117.1 130,1200 90"
            />
          </g>
        </svg>
      </div>

      <!-- Sweep line -->
      <div class="sweep-line" />

      <!-- Corner decorations -->
      <span class="corner tl" />
      <span class="corner tr" />
      <span class="corner bl" />
      <span class="corner br" />
    </div>

    <!-- Labels -->
    <div class="loading-info">
      <div class="brand-glyph">〜</div>
      <h1 class="brand-title">LAB ACÚSTICO</h1>
      <p class="brand-sub">Modelado de Cuerdas</p>

      <div class="dots-row">
        <span class="dot" style="animation-delay: 0s" />
        <span class="dot" style="animation-delay: 0.2s" />
        <span class="dot" style="animation-delay: 0.4s" />
      </div>
      <p class="status-text">INICIALIZANDO SISTEMA</p>
    </div>
  </div>
</template>

<script setup>
// No props needed — purely presentational
</script>

<style scoped>
.loading-screen {
  position: fixed;
  inset: 0;
  z-index: 8000;
  background: var(--bg-deep, #060b18);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 32px;
}

/* ─── Oscilloscope frame ──────────────────────────────────────── */
.osc-frame {
  position: relative;
  width: min(560px, 90vw);
  height: 180px;
  border: 1.5px solid rgba(0, 212, 170, 0.3);
  border-radius: 12px;
  background: #030912;
  overflow: hidden;
  box-shadow:
    0 0 0 1px rgba(0, 212, 170, 0.06),
    0 0 40px rgba(0, 212, 170, 0.06),
    inset 0 0 40px rgba(0, 0, 0, 0.5);
}

/* CRT scanlines effect */
.crt-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  pointer-events: none;
  background: repeating-linear-gradient(
    to bottom,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.08) 2px,
    rgba(0, 0, 0, 0.08) 4px
  );
}

/* Grid */
.osc-grid {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* Wave clip container */
.wave-clip {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.wave-svg {
  position: absolute;
  top: 0;
  left: 0;
  /* Extra width to allow the animation to slide — must match viewBox */
  width: 100%;
  height: 100%;
  overflow: visible;
}

/* Ghost trace */
.wave-ghost-g {
  animation: wave-scroll 2.4s linear infinite;
}
.wave-ghost {
  fill: none;
  stroke: rgba(0, 212, 170, 0.18);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
}

/* Main trace */
.wave-main-g {
  animation: wave-scroll 2.4s linear infinite;
}
.wave-main {
  fill: none;
  stroke: #00d4aa;
  stroke-width: 2.2;
  vector-effect: non-scaling-stroke;
}

@keyframes wave-scroll {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-300px);
  }
}

/* Sweep line */
.sweep-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 2px;
  height: 100%;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(245, 200, 66, 0.5) 50%,
    transparent
  );
  animation: sweep 3s linear infinite;
  z-index: 5;
}
@keyframes sweep {
  from {
    left: -4px;
    opacity: 0;
  }
  5% {
    opacity: 1;
  }
  95% {
    opacity: 0.6;
  }
  to {
    left: calc(100% + 4px);
    opacity: 0;
  }
}

/* Corner brackets */
.corner {
  position: absolute;
  width: 10px;
  height: 10px;
  border-color: var(--teal, #00d4aa);
  border-style: solid;
  opacity: 0.6;
}
.corner.tl {
  top: 6px;
  left: 6px;
  border-width: 1.5px 0 0 1.5px;
}
.corner.tr {
  top: 6px;
  right: 6px;
  border-width: 1.5px 1.5px 0 0;
}
.corner.bl {
  bottom: 6px;
  left: 6px;
  border-width: 0 0 1.5px 1.5px;
}
.corner.br {
  bottom: 6px;
  right: 6px;
  border-width: 0 1.5px 1.5px 0;
}

/* ─── Labels ───────────────────────────────────────────────────── */
.loading-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.brand-glyph {
  font-size: 36px;
  color: var(--teal, #00d4aa);
  animation: pulse-glyph 2s ease-in-out infinite;
  line-height: 1;
}
@keyframes pulse-glyph {
  0%,
  100% {
    opacity: 0.7;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.08);
  }
}

.brand-title {
  font-family: var(--font-display, "Bebas Neue", sans-serif);
  font-size: 32px;
  letter-spacing: 0.18em;
  color: var(--text-primary, #eef2ff);
  margin: 0;
  line-height: 1;
}

.brand-sub {
  font-size: 12px;
  color: var(--text-muted, #5a6a9a);
  letter-spacing: 0.06em;
  margin: 0;
}

.dots-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--teal, #00d4aa);
  animation: dot-pulse 1.2s ease-in-out infinite both;
}
@keyframes dot-pulse {
  0%,
  80%,
  100% {
    opacity: 0.2;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.status-text {
  font-family: var(--font-mono, "Space Mono", monospace);
  font-size: 10px;
  letter-spacing: 0.2em;
  color: rgba(0, 212, 170, 0.5);
  margin: 0;
}
</style>
