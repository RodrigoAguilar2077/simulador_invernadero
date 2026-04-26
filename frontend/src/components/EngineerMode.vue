<template>
  <div class="engineer-mode">
    <div class="engineer-mode__header" @click="toggle">
      <div class="engineer-mode__label">
        <span>🔬</span>
        <span class="engineer-mode__title">Modo Ingeniero</span>
        <span class="engineer-mode__hint">{{ active ? 'Ocultar detalles' : 'Ver ecuaciones y método' }}</span>
      </div>
      <div class="toggle-switch" :class="{ 'toggle-switch--active': active }">
        <div class="toggle-switch__knob"></div>
      </div>
    </div>

    <Transition name="expand">
      <div v-if="active" class="engineer-mode__content fade-in">
        <div class="engineer-mode__grid">
          <!-- Laplace -->
          <div class="engineer-mode__card glass-card">
            <div class="engineer-mode__card-badge engineer-mode__card-badge--amber">Transformada de Laplace</div>
            <h4 class="engineer-mode__card-title">Análisis de Estabilidad</h4>
            <p class="engineer-mode__card-text">
              Analizamos la función de transferencia del invernadero para entender
              cuánta <strong>inercia térmica</strong> tiene según el material elegido.
            </p>
            <div class="engineer-mode__equation">
              <div class="eq-line">H(s) = k / (s + k)</div>
              <div class="eq-desc">Función de transferencia de primer orden</div>
            </div>
            <ul class="engineer-mode__list">
              <li><strong>τ = 1/k</strong> — Constante de tiempo (Time Constant)</li>
              <li><strong>Polo: s = -k</strong> — Siempre estable (semiplano izquierdo)</li>
              <li>Si τ es <span class="text-red">pequeño</span> → sistema RÁPIDO, el calor se escapa fácil</li>
              <li>Si τ es <span class="text-blue">grande</span> → sistema LENTO, excelente retención</li>
            </ul>
          </div>

          <!-- Euler -->
          <div class="engineer-mode__card glass-card">
            <div class="engineer-mode__card-badge engineer-mode__card-badge--green">Euler Mejorado (Heun)</div>
            <h4 class="engineer-mode__card-title">Resolución Numérica</h4>
            <p class="engineer-mode__card-text">
              Tomamos los datos climáticos reales de la ciudad elegida y resolvemos
              la ecuación diferencial de calor <strong>cada 60 segundos</strong>.
            </p>
            <div class="engineer-mode__equation">
              <div class="eq-line">dT/dt = k(T_ext − T_int) + α·Rad(t)</div>
              <div class="eq-desc">Ley de Enfriamiento de Newton + Radiación</div>
            </div>
            <div class="engineer-mode__steps">
              <div class="step">
                <span class="step__num">1</span>
                <span class="step__text"><strong>Predictor:</strong> T̃ = T + h·f(t, T)</span>
              </div>
              <div class="step">
                <span class="step__num">2</span>
                <span class="step__text"><strong>Corrector:</strong> T_{n+1} = T + (h/2)[f₁ + f₂]</span>
              </div>
              <div class="step">
                <span class="step__num">3</span>
                <span class="step__text">Repetir para cada minuto del día</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Laplace Analysis Results -->
        <div v-if="laplaceData" class="engineer-mode__results glass-card fade-in">
          <h4 class="engineer-mode__results-title">📊 Resultados del Análisis — {{ laplaceData.material_nombre }}</h4>
          <div class="engineer-mode__results-grid">
            <div class="engineer-mode__results-col">
              <div class="stat-row">
                <span class="stat-label">Constante τ</span>
                <span class="stat-value stat-value--green">{{ laplaceData.tau_minutos }} min</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">τ en horas</span>
                <span class="stat-value">{{ laplaceData.tau_horas }} h</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Polo s</span>
                <span class="stat-value stat-value--amber">{{ laplaceData.polo }}</span>
              </div>
            </div>
            <div class="engineer-mode__results-col">
              <div class="stat-row">
                <span class="stat-label">Ganancia DC</span>
                <span class="stat-value">{{ laplaceData.ganancia_estatica }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Estabilización (4τ)</span>
                <span class="stat-value stat-value--blue">{{ laplaceData.tiempo_estabilizacion_horas }} h</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Clasificación</span>
                <span class="badge" :class="`badge--${laplaceData.clasificacion}`">{{ laplaceData.clasificacion }}</span>
              </div>
            </div>
          </div>
          <div class="engineer-mode__desc">
            <p>{{ laplaceData.descripcion }}</p>
          </div>
          <div v-if="laplaceData.step_response_t" class="engineer-mode__step-chart">
            <div class="tf-label">Respuesta al Escalón Unitario</div>
            <div class="step-chart-wrap">
              <Line :data="stepChartData" :options="stepChartOptions" />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  PointElement, LineElement, Filler, Tooltip,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip)

const props = defineProps({
  laplaceData: { type: Object, default: null },
})

const active = ref(false)

function toggle() { active.value = !active.value }

const stepChartData = computed(() => {
  if (!props.laplaceData?.step_response_t) return { labels: [], datasets: [] }
  const t = props.laplaceData.step_response_t
  const y = props.laplaceData.step_response_y
  const step = Math.max(1, Math.floor(t.length / 80))
  return {
    labels: t.filter((_, i) => i % step === 0).map(v => v.toFixed(0)),
    datasets: [{
      data: y.filter((_, i) => i % step === 0),
      borderColor: '#4ade80', backgroundColor: 'rgba(74,222,128,0.08)',
      borderWidth: 2, pointRadius: 0, tension: 0.4, fill: true,
    }],
  }
})

const stepChartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: {
    backgroundColor: 'rgba(15,23,36,0.95)', bodyColor: '#94a3b8',
    borderColor: 'rgba(148,163,184,0.15)', borderWidth: 1, padding: 8, cornerRadius: 6,
  }},
  scales: {
    x: { grid: { display: false }, ticks: { color: '#475569', font: { size: 9 }, maxTicksLimit: 5 },
      title: { display: true, text: 'min', color: '#64748b', font: { size: 9 } } },
    y: { grid: { color: 'rgba(148,163,184,0.06)' }, ticks: { color: '#475569', font: { size: 9 }, maxTicksLimit: 4 }, min: 0, max: 1.1 },
  },
}
</script>

<style scoped>
.engineer-mode { margin-top: var(--space-lg); }
.engineer-mode__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  background: var(--glass-bg); border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg); cursor: pointer;
  transition: all var(--transition-base);
}
.engineer-mode__header:hover { border-color: var(--glass-border-hover); }
.engineer-mode__label { display: flex; align-items: center; gap: var(--space-sm); }
.engineer-mode__title { font-weight: 700; font-size: var(--font-size-sm); }
.engineer-mode__hint { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.engineer-mode__content { margin-top: var(--space-md); }
.engineer-mode__grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-lg); margin-bottom: var(--space-lg); }
.engineer-mode__card { padding: var(--space-lg); }
.engineer-mode__card-badge {
  display: inline-block; padding: 2px 12px; border-radius: var(--radius-full);
  font-size: var(--font-size-xs); font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin-bottom: var(--space-sm);
}
.engineer-mode__card-badge--amber { background: rgba(251,191,36,0.12); color: var(--color-amber-400); }
.engineer-mode__card-badge--green { background: rgba(74,222,128,0.12); color: var(--color-green-400); }
.engineer-mode__card-title { font-size: var(--font-size-base); font-weight: 700; margin-bottom: var(--space-sm); }
.engineer-mode__card-text { font-size: var(--font-size-sm); color: var(--color-text-secondary); line-height: 1.6; margin-bottom: var(--space-md); }
.engineer-mode__equation {
  padding: var(--space-md); background: rgba(0,0,0,0.3);
  border-radius: var(--radius-sm); margin-bottom: var(--space-md); text-align: center;
}
.eq-line { font-family: 'Courier New', monospace; font-size: var(--font-size-lg); color: var(--color-green-300); font-weight: 600; word-break: break-word; }
.eq-desc { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: var(--space-xs); }
.engineer-mode__list {
  list-style: none; display: flex; flex-direction: column; gap: var(--space-xs);
  font-size: var(--font-size-sm); color: var(--color-text-secondary);
}
.engineer-mode__list li::before { content: '→ '; color: var(--color-green-400); }
.text-red { color: var(--color-red-400); font-weight: 600; }
.text-blue { color: var(--color-blue-400); font-weight: 600; }
.engineer-mode__steps { display: flex; flex-direction: column; gap: var(--space-sm); }
.step { display: flex; align-items: center; gap: var(--space-sm); }
.step__num {
  width: 24px; height: 24px; border-radius: 50%;
  background: rgba(74,222,128,0.15); color: var(--color-green-400);
  font-size: var(--font-size-xs); font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step__text { font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.engineer-mode__results { padding: var(--space-lg); }
.engineer-mode__results-title { font-size: var(--font-size-sm); font-weight: 700; margin-bottom: var(--space-md); }
.engineer-mode__results-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-lg); }
.engineer-mode__desc {
  margin-top: var(--space-md); padding: var(--space-sm);
  background: rgba(74,222,128,0.04); border-radius: var(--radius-sm);
  border-left: 2px solid var(--color-green-500);
  font-size: var(--font-size-xs); color: var(--color-text-secondary); line-height: 1.6;
}
.engineer-mode__step-chart { margin-top: var(--space-md); }
.tf-label { font-size: var(--font-size-xs); color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: var(--space-xs); }
.step-chart-wrap { height: 140px; position: relative; width: 100%; min-width: 0; }
.expand-enter-active, .expand-leave-active { transition: all 0.4s ease; }
.expand-enter-from, .expand-leave-to { opacity: 0; transform: translateY(-10px); }

@media (max-width: 768px) {
  .engineer-mode__grid { grid-template-columns: 1fr; }
  .engineer-mode__results-grid { grid-template-columns: 1fr; }
}
</style>
