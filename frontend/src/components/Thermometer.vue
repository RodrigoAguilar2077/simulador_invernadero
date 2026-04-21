<template>
  <div class="thermometer-container">
    <h3 class="section-title">
      <span class="section-title__icon">🌡️</span>
      Temperatura
    </h3>
    <div class="thermometer-body pulse-glow">
      <svg viewBox="0 0 80 220" class="thermometer-svg">
        <!-- Bulbo inferior -->
        <circle
          cx="40" cy="190"
          r="22"
          :fill="tempGradientUrl"
          stroke="rgba(148, 163, 184, 0.2)"
          stroke-width="1.5"
        />
        <!-- Tubo -->
        <rect
          x="30" y="20"
          width="20" height="170"
          rx="10"
          fill="rgba(22, 32, 50, 0.6)"
          stroke="rgba(148, 163, 184, 0.2)"
          stroke-width="1.5"
        />
        <!-- Nivel de mercurio (animado) -->
        <rect
          x="33" :y="mercuryY"
          width="14"
          :height="mercuryHeight"
          rx="7"
          :fill="tempGradientUrl"
          class="mercury-bar"
        />
        <!-- Marcas de escala -->
        <g v-for="mark in scaleMarks" :key="mark.temp">
          <line
            :x1="52" :y1="mark.y"
            :x2="58" :y2="mark.y"
            stroke="rgba(148, 163, 184, 0.3)"
            stroke-width="1"
          />
          <text
            :x="62" :y="mark.y + 4"
            fill="#64748b"
            font-size="9"
            font-family="Inter"
          >{{ mark.temp }}°</text>
        </g>
        <!-- Gradientes -->
        <defs>
          <linearGradient :id="gradientId" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0%" :stop-color="coldColor" />
            <stop offset="50%" :stop-color="midColor" />
            <stop offset="100%" :stop-color="hotColor" />
          </linearGradient>
        </defs>
      </svg>
      <div class="thermometer-value">
        <span class="thermometer-temp" :style="{ color: currentColor }">
          {{ displayTemp }}
        </span>
        <span class="thermometer-unit">°C</span>
      </div>
      <div class="thermometer-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  temperature: { type: Number, default: 15 },
  label: { type: String, default: 'Interior' },
})

const gradientId = ref(`therm-grad-${Math.random().toString(36).slice(2)}`)

// Rango de temperatura del termómetro
const T_MIN = -10
const T_MAX = 50
const TUBE_TOP = 25
const TUBE_BOTTOM = 185

const displayTemp = computed(() => props.temperature.toFixed(1))

const normalizedTemp = computed(() => {
  return Math.max(0, Math.min(1, (props.temperature - T_MIN) / (T_MAX - T_MIN)))
})

const mercuryHeight = computed(() => {
  const maxHeight = TUBE_BOTTOM - TUBE_TOP
  return Math.max(14, normalizedTemp.value * maxHeight)
})

const mercuryY = computed(() => {
  return TUBE_BOTTOM - mercuryHeight.value
})

const scaleMarks = computed(() => {
  const marks = []
  for (let t = 0; t <= 40; t += 10) {
    const norm = (t - T_MIN) / (T_MAX - T_MIN)
    const y = TUBE_BOTTOM - norm * (TUBE_BOTTOM - TUBE_TOP)
    marks.push({ temp: t, y })
  }
  return marks
})

const coldColor = '#3b82f6'
const midColor = '#22c55e'
const hotColor = '#ef4444'
const tempGradientUrl = computed(() => `url(#${gradientId.value})`)

const currentColor = computed(() => {
  const t = normalizedTemp.value
  if (t < 0.33) return coldColor
  if (t < 0.66) return midColor
  return hotColor
})
</script>

<style scoped>
.thermometer-container {
  padding: var(--space-lg);
}

.thermometer-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

.thermometer-svg {
  width: 80px;
  height: 200px;
}

.mercury-bar {
  transition: y 1s ease, height 1s ease;
}

.thermometer-value {
  display: flex;
  align-items: baseline;
  gap: 2px;
  margin-top: var(--space-xs);
}

.thermometer-temp {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  transition: color 0.5s ease;
  line-height: 1;
}

.thermometer-unit {
  font-size: var(--font-size-lg);
  color: var(--color-text-muted);
  font-weight: 400;
}

.thermometer-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
</style>
