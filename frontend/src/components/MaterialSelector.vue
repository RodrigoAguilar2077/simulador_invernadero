<template>
  <div class="material-selector">
    <h3 class="section-title">
      <span class="section-title__icon">🧪</span>
      Materiales
    </h3>
    <div class="material-list">
      <div
        v-for="material in materials"
        :key="material.id"
        class="material-card"
        :class="{ 'material-card--selected': isSelected(material.id) }"
        @click="toggleMaterial(material.id)"
      >
        <div class="material-card__checkbox"></div>
        <div class="material-card__info">
          <div class="material-card__name">{{ material.nombre }}</div>
          <div class="material-card__detail">
            U={{ material.U }} W/m²·K · τ={{ material.transmitancia_solar }}
          </div>
        </div>
      </div>
    </div>

    <div class="dimension-controls">
      <h3 class="section-title" style="margin-top: var(--space-lg);">
        <span class="section-title__icon">📐</span>
        Dimensiones
      </h3>

      <div class="form-group">
        <div class="slider-header">
          <label class="form-label">Largo</label>
          <span class="form-value">{{ dimensions.largo }} m</span>
        </div>
        <input
          type="range"
          class="slider-input"
          v-model.number="dimensions.largo"
          min="3" max="50" step="1"
        />
      </div>

      <div class="form-group">
        <div class="slider-header">
          <label class="form-label">Ancho</label>
          <span class="form-value">{{ dimensions.ancho }} m</span>
        </div>
        <input
          type="range"
          class="slider-input"
          v-model.number="dimensions.ancho"
          min="2" max="30" step="1"
        />
      </div>

      <div class="form-group">
        <div class="slider-header">
          <label class="form-label">Alto</label>
          <span class="form-value">{{ dimensions.alto }} m</span>
        </div>
        <input
          type="range"
          class="slider-input"
          v-model.number="dimensions.alto"
          min="2" max="8" step="0.5"
        />
      </div>

      <div class="form-group">
        <div class="slider-header">
          <label class="form-label">Temperatura Inicial</label>
          <span class="form-value">{{ dimensions.T_inicial }}°C</span>
        </div>
        <input
          type="range"
          class="slider-input"
          v-model.number="dimensions.T_inicial"
          min="-5" max="40" step="1"
        />
      </div>

      <div class="form-group">
        <div class="slider-header">
          <label class="form-label">Horas de Simulación</label>
          <span class="form-value">{{ dimensions.horas }}h</span>
        </div>
        <input
          type="range"
          class="slider-input"
          v-model.number="dimensions.horas"
          min="1" max="72" step="1"
        />
      </div>
    </div>

    <button
      class="btn btn--primary btn--full simulate-btn"
      :disabled="selectedMaterials.length === 0 || loading"
      @click="$emit('simulate')"
    >
      <span v-if="loading" class="spinner"></span>
      <span v-else>▶</span>
      {{ loading ? 'Simulando...' : 'Simular' }}
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  materials: { type: Array, default: () => [] },
  selectedMaterials: { type: Array, default: () => [] },
  dimensions: {
    type: Object,
    default: () => ({
      largo: 10,
      ancho: 5,
      alto: 3,
      T_inicial: 15,
      horas: 24,
    }),
  },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['toggle-material', 'simulate'])

function isSelected(materialId) {
  return props.selectedMaterials.includes(materialId)
}

function toggleMaterial(materialId) {
  emit('toggle-material', materialId)
}
</script>

<style scoped>
.material-selector {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: var(--space-lg);
  height: 100%;
  overflow-y: auto;
}

.material-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.dimension-controls {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.simulate-btn {
  margin-top: var(--space-lg);
  padding: var(--space-md) var(--space-lg);
  font-size: var(--font-size-base);
}
</style>
