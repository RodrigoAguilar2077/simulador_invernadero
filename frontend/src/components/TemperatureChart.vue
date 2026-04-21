<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3 class="section-title">
        <span class="section-title__icon">📈</span>
        Simulación Térmica
      </h3>
      <div class="chart-legend" v-if="hasData">
        <div class="legend-item">
          <span class="legend-dot" style="background: rgba(251, 191, 36, 0.8);"></span>
          <span class="legend-label">T. Exterior</span>
        </div>
        <div
          v-for="sim in simulationData.simulaciones"
          :key="sim.material_id"
          class="legend-item"
        >
          <span class="legend-dot" :style="{ background: sim.color }"></span>
          <span class="legend-label">{{ sim.material_nombre }}</span>
        </div>
      </div>
    </div>

    <div class="chart-wrapper" v-if="hasData">
      <Line :data="chartData" :options="chartOptions" />
    </div>

    <div class="chart-placeholder" v-else>
      <div class="placeholder-icon">🌡️</div>
      <p class="placeholder-text">
        Selecciona materiales y presiona <strong>Simular</strong> para ver la curva térmica
      </p>
    </div>

    <!-- Stats Row -->
    <div class="chart-stats" v-if="hasData">
      <div
        class="chart-stat-card glass-card--static"
        v-for="sim in simulationData.simulaciones"
        :key="'stat-' + sim.material_id"
      >
        <div class="chart-stat-header" :style="{ borderLeftColor: sim.color }">
          {{ sim.material_nombre }}
        </div>
        <div class="chart-stat-grid">
          <div class="stat-row">
            <span class="stat-label">T. Máxima</span>
            <span class="stat-value stat-value--red">{{ sim.T_max_int }}°C</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">T. Mínima</span>
            <span class="stat-value stat-value--blue">{{ sim.T_min_int }}°C</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">T. Promedio</span>
            <span class="stat-value stat-value--green">{{ sim.T_promedio_int }}°C</span>
          </div>
        </div>
      </div>
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
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  simulationData: { type: Object, default: null },
})

const hasData = computed(() => {
  return props.simulationData && props.simulationData.simulaciones && props.simulationData.simulaciones.length > 0
})

const chartData = computed(() => {
  if (!hasData.value) return { labels: [], datasets: [] }

  const data = props.simulationData
  // Reduce points for performance: show every 5th minute instead of all 1440
  const step = Math.max(1, Math.floor(data.tiempo_horas.length / 300))
  const labels = data.tiempo_horas
    .filter((_, i) => i % step === 0)
    .map(h => {
      const hours = Math.floor(h)
      const mins = Math.round((h - hours) * 60)
      return `${hours}:${mins.toString().padStart(2, '0')}`
    })

  // Exterior temperature dataset
  const datasets = [
    {
      label: 'T. Exterior',
      data: data.T_exterior.filter((_, i) => i % step === 0),
      borderColor: 'rgba(251, 191, 36, 0.8)',
      backgroundColor: 'rgba(251, 191, 36, 0.05)',
      borderWidth: 2,
      borderDash: [8, 4],
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.4,
      fill: false,
    },
  ]

  // Interior temperature for each material
  for (const sim of data.simulaciones) {
    datasets.push({
      label: sim.material_nombre,
      data: sim.T_interior.filter((_, i) => i % step === 0),
      borderColor: sim.color,
      backgroundColor: hexToRgba(sim.color, 0.08),
      borderWidth: 2.5,
      pointRadius: 0,
      pointHoverRadius: 5,
      tension: 0.4,
      fill: true,
    })
  }

  return { labels, datasets }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 36, 0.95)',
      titleColor: '#f0f4f8',
      bodyColor: '#94a3b8',
      borderColor: 'rgba(148, 163, 184, 0.15)',
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8,
      titleFont: { family: 'Inter', weight: '600', size: 13 },
      bodyFont: { family: 'Inter', size: 12 },
      callbacks: {
        label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}°C`,
      },
    },
  },
  scales: {
    x: {
      grid: { color: 'rgba(148, 163, 184, 0.06)', drawBorder: false },
      ticks: {
        color: '#64748b',
        font: { family: 'Inter', size: 11 },
        maxTicksLimit: 13,
      },
      title: {
        display: true,
        text: 'Hora del día',
        color: '#94a3b8',
        font: { family: 'Inter', size: 12, weight: '500' },
      },
    },
    y: {
      grid: { color: 'rgba(148, 163, 184, 0.06)', drawBorder: false },
      ticks: {
        color: '#64748b',
        font: { family: 'Inter', size: 11 },
        callback: (v) => `${v}°C`,
      },
      title: {
        display: true,
        text: 'Temperatura (°C)',
        color: '#94a3b8',
        font: { family: 'Inter', size: 12, weight: '500' },
      },
    },
  },
}))

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
</script>

<style scoped>
.chart-container {
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  height: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.chart-wrapper {
  flex: 1;
  min-height: 350px;
  position: relative;
}

.chart-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 350px;
  gap: var(--space-md);
}

.placeholder-icon {
  font-size: 3rem;
  opacity: 0.3;
}

.placeholder-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  text-align: center;
  max-width: 280px;
  line-height: 1.7;
}

.chart-stats {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.chart-stat-card {
  flex: 1;
  min-width: 180px;
  padding: var(--space-md);
}

.chart-stat-header {
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding-bottom: var(--space-sm);
  margin-bottom: var(--space-sm);
  border-left: 3px solid;
  padding-left: var(--space-sm);
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.chart-stat-grid {
  display: flex;
  flex-direction: column;
}
</style>
