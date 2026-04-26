<template>
  <div class="laplace-panel">
    <h3 class="section-title">
      <span class="section-title__icon">📊</span>
      Análisis de Laplace
    </h3>

    <div v-if="analysis" class="laplace-content fade-in">

      <div class="laplace-classification">
        <span
          class="badge"
          :class="`badge--${analysis.clasificacion}`"
        >
          {{ analysis.clasificacion }}
        </span>
      </div>


      <div class="transfer-function">
        <div class="tf-label">Función de Transferencia</div>
        <div class="tf-equation">
          H(s) = k / (s + k)
        </div>
      </div>


      <div class="laplace-stats">
        <div class="stat-row">
          <span class="stat-label">Constante τ</span>
          <span class="stat-value stat-value--green">
            {{ analysis.tau_minutos }} min
          </span>
        </div>
        <div class="stat-row">
          <span class="stat-label">τ en horas</span>
          <span class="stat-value">{{ analysis.tau_horas }} h</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Polo s</span>
          <span class="stat-value stat-value--amber">
            {{ analysis.polo }}
          </span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Ganancia DC</span>
          <span class="stat-value">{{ analysis.ganancia_estatica }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Estabilización (4τ)</span>
          <span class="stat-value stat-value--blue">
            {{ analysis.tiempo_estabilizacion_horas }} h
          </span>
        </div>
      </div>


      <div class="laplace-description">
        <p>{{ analysis.descripcion }}</p>
      </div>


      <div class="step-response-chart" v-if="analysis.step_response_t">
        <div class="tf-label" style="margin-bottom: 8px;">Respuesta al Escalón</div>
        <div class="step-chart-wrapper">
          <Line :data="stepChartData" :options="stepChartOptions" />
        </div>
      </div>
    </div>

    <div v-else class="laplace-empty">
      <p class="placeholder-text">
        Ejecuta una simulación para ver el análisis de transferencia
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip)

const props = defineProps({
  analysis: { type: Object, default: null },
})

const stepChartData = computed(() => {
  if (!props.analysis?.step_response_t) return { labels: [], datasets: [] }

  const t = props.analysis.step_response_t
  const y = props.analysis.step_response_y
  const step = Math.max(1, Math.floor(t.length / 80))

  return {
    labels: t.filter((_, i) => i % step === 0).map(v => v.toFixed(0)),
    datasets: [
      {
        data: y.filter((_, i) => i % step === 0),
        borderColor: '#4ade80',
        backgroundColor: 'rgba(74, 222, 128, 0.08)',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4,
        fill: true,
      },
    ],
  }
})

const stepChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 36, 0.95)',
      titleColor: '#f0f4f8',
      bodyColor: '#94a3b8',
      borderColor: 'rgba(148, 163, 184, 0.15)',
      borderWidth: 1,
      padding: 8,
      cornerRadius: 6,
      bodyFont: { family: 'Inter', size: 11 },
    },
  },
  scales: {
    x: {
      display: true,
      grid: { display: false },
      ticks: {
        color: '#475569',
        font: { size: 9 },
        maxTicksLimit: 5,
      },
      title: {
        display: true,
        text: 'min',
        color: '#64748b',
        font: { size: 9 },
      },
    },
    y: {
      display: true,
      grid: { color: 'rgba(148, 163, 184, 0.06)' },
      ticks: {
        color: '#475569',
        font: { size: 9 },
        maxTicksLimit: 4,
      },
      min: 0,
      max: 1.1,
    },
  },
}
</script>

<style scoped>
.laplace-panel {
  padding: var(--space-lg);
}

.laplace-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.laplace-classification {
  text-align: center;
}

.transfer-function {
  text-align: center;
  padding: var(--space-md);
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  border: 1px solid rgba(148, 163, 184, 0.06);
}

.tf-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-xs);
}

.tf-equation {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-green-300);
  font-family: 'Courier New', monospace;
}

.laplace-stats {
  display: flex;
  flex-direction: column;
}

.laplace-description {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  line-height: 1.6;
  padding: var(--space-sm);
  background: rgba(74, 222, 128, 0.04);
  border-radius: var(--radius-sm);
  border-left: 2px solid var(--color-green-500);
}

.step-chart-wrapper {
  height: 120px;
  position: relative;
}

.laplace-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.placeholder-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-align: center;
}
</style>
