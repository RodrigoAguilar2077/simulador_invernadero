<template>
  <div class="weather-info" :class="{ 'weather-info--compact': compact }">
    <template v-if="compact">

      <div v-if="weather" class="weather-compact">
        <img
          :src="`https://openweathermap.org/img/wn/${weather.icono}.png`"
          :alt="weather.descripcion"
          width="32" height="32" class="weather-compact__icon"
        />
        <span class="weather-compact__temp">{{ weather.temp.toFixed(1) }}°C</span>
        <span class="weather-compact__city"><MapPin size="12" style="display:inline; margin-right:2px"/>{{ weather.ciudad }}</span>
        <span class="weather-compact__desc">{{ weather.descripcion }}</span>
      </div>
      <div v-else-if="error" class="weather-compact weather-compact--error">
        <span>{{ error }}</span>
      </div>
      <div v-else class="weather-compact">
        <div class="spinner" style="width:16px;height:16px"></div>
        <span class="weather-compact__desc">Cargando clima...</span>
      </div>
    </template>

    <template v-else>

      <h3 class="section-title">
        <span class="section-title__icon"><CloudSun size="24" /></span>
        Clima Actual
      </h3>

      <div v-if="weather" class="weather-content fade-in">
        <div class="weather-main">
          <div class="weather-icon gentle-bounce">
            <img
              :src="`https://openweathermap.org/img/wn/${weather.icono}@2x.png`"
              :alt="weather.descripcion"
              width="64" height="64"
            />
          </div>
          <div class="weather-temp-block">
            <span class="weather-temp">{{ weather.temp.toFixed(1) }}</span>
            <span class="weather-unit">°C</span>
          </div>
        </div>
        <div class="weather-description">{{ weather.descripcion }}</div>
        <div class="weather-city"><MapPin size="14" style="display:inline; margin-right:2px"/>{{ weather.ciudad }}</div>
        <div class="weather-details">
          <div class="stat-row">
            <span class="stat-label">Sensación</span>
            <span class="stat-value">{{ weather.feels_like.toFixed(1) }}°C</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Humedad</span>
            <span class="stat-value stat-value--blue">{{ weather.humedad }}%</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Nubosidad</span>
            <span class="stat-value">{{ weather.nubosidad }}%</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Viento</span>
            <span class="stat-value">{{ weather.viento_velocidad }} m/s</span>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="weather-error">
        <p>{{ error }}</p>
      </div>

      <div v-else class="weather-loading">
        <div class="spinner"></div>
        <p class="placeholder-text">Cargando clima...</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { MapPin, CloudSun } from 'lucide-vue-next'

defineProps({
  weather: { type: Object, default: null },
  error: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})
</script>

<style scoped>
/* Compact */
.weather-compact {
  display: flex; align-items: center; gap: var(--space-sm);
  font-size: var(--font-size-sm);
}
.weather-compact__icon { filter: drop-shadow(0 0 4px rgba(251,191,36,0.3)); }
.weather-compact__temp { font-weight: 700; color: var(--color-amber-400); }
.weather-compact__city { color: var(--color-text-secondary); font-size: var(--font-size-xs); }
.weather-compact__desc { color: var(--color-text-muted); font-size: var(--font-size-xs); text-transform: capitalize; }
.weather-compact--error { color: var(--color-red-400); font-size: var(--font-size-xs); }

/* Full */
.weather-info:not(.weather-info--compact) { padding: var(--space-lg); }
.weather-content { display:flex; flex-direction:column; align-items:center; gap: var(--space-sm); }
.weather-main { display:flex; align-items:center; gap: var(--space-sm); }
.weather-icon img { filter: drop-shadow(0 0 8px rgba(251,191,36,0.3)); }
.weather-temp-block { display:flex; align-items:baseline; gap:2px; }
.weather-temp { font-size: var(--font-size-3xl); font-weight:800; color: var(--color-amber-400); line-height:1; }
.weather-unit { font-size: var(--font-size-lg); color: var(--color-text-muted); }
.weather-description { font-size: var(--font-size-sm); color: var(--color-text-secondary); text-transform:capitalize; }
.weather-city { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.weather-details { width:100%; margin-top: var(--space-sm); }
.weather-error { text-align:center; padding: var(--space-lg); font-size: var(--font-size-xs); color: var(--color-red-400); }
.weather-loading { display:flex; flex-direction:column; align-items:center; gap: var(--space-md); padding: var(--space-xl); }
</style>
