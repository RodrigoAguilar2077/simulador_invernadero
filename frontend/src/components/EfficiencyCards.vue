<template>
  <div class="efficiency-cards">
    <h3 class="section-title">
      <span class="section-title__icon">⚡</span>
      Eficiencia Energética
    </h3>

    <div v-if="loading" class="efficiency-grid">
      <div v-for="i in 3" :key="i" class="efficiency-skeleton glass-card--static">
        <div class="skeleton" style="height:16px;width:60%;margin-bottom:12px"></div>
        <div class="skeleton" style="height:8px;width:100%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:24px;width:40%"></div>
      </div>
    </div>

    <div v-else-if="simulationData && simulationData.simulaciones" class="efficiency-grid">
      <div
        v-for="(sim, idx) in simulationData.simulaciones"
        :key="sim.material_id"
        class="efficiency-card glass-card fade-in-up"
        :style="{ animationDelay: (idx * 0.12) + 's' }"
      >
        <div class="efficiency-card__header">
          <div class="efficiency-card__dot" :style="{ background: sim.color }"></div>
          <span class="efficiency-card__name">{{ sim.material_nombre }}</span>
        </div>

        <div class="efficiency-card__metrics">
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
            <span class="stat-value stat-value--purple">{{ sim.T_promedio_int }}°C</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">ΔT (max-min)</span>
            <span class="stat-value stat-value--amber">
              {{ (sim.T_max_int - sim.T_min_int).toFixed(1) }}°C
            </span>
          </div>
        </div>

        <div class="efficiency-card__gauge">
          <div class="gauge-label">Retención Térmica</div>
          <div class="gauge-bar">
            <div
              class="gauge-fill"
              :style="{
                width: retentionPercent(sim) + '%',
                background: retentionColor(sim)
              }"
            ></div>
          </div>
          <div class="gauge-value">{{ retentionPercent(sim) }}%</div>
        </div>
      </div>
    </div>

    <div v-else class="efficiency-empty">
      <p class="placeholder-text">Ejecuta una simulación para ver las métricas de eficiencia</p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  simulationData: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

function retentionPercent(sim) {
  const delta = sim.T_max_int - sim.T_min_int
  const pct = Math.max(10, Math.min(100, 100 - (delta / 30) * 90))
  return Math.round(pct)
}

function retentionColor(sim) {
  const pct = retentionPercent(sim)
  if (pct >= 70) return 'var(--color-purple-400)'
  if (pct >= 45) return 'var(--color-amber-400)'
  return 'var(--color-red-400)'
}
</script>

<style scoped>
.efficiency-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-md);
}
.efficiency-card { padding: var(--space-lg); }
.efficiency-card__header {
  display: flex; align-items: center; gap: var(--space-sm);
  margin-bottom: var(--space-md); padding-bottom: var(--space-sm);
  border-bottom: 1px solid rgba(148,163,184,0.08);
}
.efficiency-card__dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.efficiency-card__name { font-size: var(--font-size-sm); font-weight: 700; }
.efficiency-card__metrics { margin-bottom: var(--space-md); }
.efficiency-card__gauge { margin-top: var(--space-sm); }
.gauge-label { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-bottom: var(--space-xs); }
.gauge-bar {
  height: 6px; background: var(--color-bg-surface);
  border-radius: var(--radius-full); overflow: hidden;
}
.gauge-fill {
  height: 100%; border-radius: var(--radius-full);
  transition: width 1s ease;
}
.gauge-value {
  font-size: var(--font-size-xs); font-weight: 700;
  color: var(--color-text-secondary); margin-top: 2px; text-align: right;
}
.efficiency-skeleton { padding: var(--space-lg); }
.efficiency-empty {
  text-align: center; padding: var(--space-xl);
  color: var(--color-text-muted); font-size: var(--font-size-sm);
}
.placeholder-text { font-size: var(--font-size-xs); color: var(--color-text-muted); }
</style>
