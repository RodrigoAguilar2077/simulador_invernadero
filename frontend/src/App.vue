<template>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header glass-card--static">
      <div>
        <h1 class="app-header__title">🌿 Simulador de Invernadero</h1>
        <p class="app-header__subtitle">
          Modelado térmico con Euler Mejorado y análisis de Laplace
        </p>
      </div>
      <div class="app-header__badge">
        <span class="badge-dot"></span>
        {{ connectionStatus }}
      </div>
    </header>

    <!-- Dashboard -->
    <main class="dashboard-grid">
      <!-- Panel Izquierdo: Controles -->
      <aside class="dashboard-grid__controls glass-card">
        <MaterialSelector
          :materials="materials"
          :selectedMaterials="selectedMaterials"
          :dimensions="dimensions"
          :loading="simulating"
          @toggle-material="toggleMaterial"
          @simulate="runSimulation"
        />
      </aside>

      <!-- Centro: Gráfica Principal -->
      <section class="dashboard-grid__chart glass-card">
        <TemperatureChart :simulationData="simulationResult" />
      </section>

      <!-- Panel Derecho: Info -->
      <aside class="dashboard-grid__sidebar">
        <!-- Termómetro -->
        <div class="glass-card">
          <Thermometer
            :temperature="currentTemp"
            :label="thermometerLabel"
          />
        </div>

        <!-- Clima Actual -->
        <div class="glass-card">
          <WeatherInfo
            :weather="weatherData"
            :error="weatherError"
          />
        </div>

        <!-- Laplace -->
        <div class="glass-card">
          <LaplacePanel :analysis="laplaceData" />
        </div>
      </aside>
    </main>

    <!-- Error Toast -->
    <Transition name="toast">
      <div v-if="errorMessage" class="error-toast glass-card" @click="errorMessage = ''">
        <span>⚠️</span>
        <span>{{ errorMessage }}</span>
        <span class="toast-close">✕</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import MaterialSelector from './components/MaterialSelector.vue'
import TemperatureChart from './components/TemperatureChart.vue'
import Thermometer from './components/Thermometer.vue'
import WeatherInfo from './components/WeatherInfo.vue'
import LaplacePanel from './components/LaplacePanel.vue'
import {
  fetchMaterials,
  compareSimulation,
  fetchLaplaceAnalysis,
  fetchWeather,
} from './services/api.js'

// ============================================================
// State
// ============================================================

const materials = ref([])
const selectedMaterials = ref([])
const simulating = ref(false)
const simulationResult = ref(null)
const laplaceData = ref(null)
const weatherData = ref(null)
const weatherError = ref('')
const errorMessage = ref('')
const connectionStatus = ref('Conectando...')

const dimensions = reactive({
  largo: 10,
  ancho: 5,
  alto: 3,
  T_inicial: 15,
  horas: 24,
})

// ============================================================
// Computed
// ============================================================

const currentTemp = computed(() => {
  if (simulationResult.value?.simulaciones?.length > 0) {
    const sim = simulationResult.value.simulaciones[0]
    // Show the last simulated temperature
    return sim.T_promedio_int
  }
  if (weatherData.value) {
    return weatherData.value.temp
  }
  return dimensions.T_inicial
})

const thermometerLabel = computed(() => {
  if (simulationResult.value?.simulaciones?.length > 0) {
    return 'Prom. Interior'
  }
  return weatherData.value ? 'Exterior Actual' : 'Temp. Inicial'
})

// ============================================================
// Methods
// ============================================================

function toggleMaterial(materialId) {
  const idx = selectedMaterials.value.indexOf(materialId)
  if (idx >= 0) {
    selectedMaterials.value.splice(idx, 1)
  } else {
    selectedMaterials.value.push(materialId)
  }
}

async function runSimulation() {
  if (selectedMaterials.value.length === 0) return
  
  simulating.value = true
  errorMessage.value = ''

  try {
    // Run comparative simulation
    const result = await compareSimulation({
      material_ids: selectedMaterials.value,
      T_inicial: dimensions.T_inicial,
      horas: dimensions.horas,
      largo: dimensions.largo,
      ancho: dimensions.ancho,
      alto: dimensions.alto,
      usar_api_clima: true,
    })
    simulationResult.value = result

    // Also run Laplace analysis for the first selected material
    const laplace = await fetchLaplaceAnalysis({
      material_id: selectedMaterials.value[0],
      largo: dimensions.largo,
      ancho: dimensions.ancho,
      alto: dimensions.alto,
    })
    laplaceData.value = laplace
  } catch (err) {
    errorMessage.value = err.message
    console.error('Simulation error:', err)
  } finally {
    simulating.value = false
  }
}

async function loadInitialData() {
  try {
    // Load materials
    const mats = await fetchMaterials()
    materials.value = mats
    connectionStatus.value = 'API Conectada'

    // Load weather
    try {
      const weather = await fetchWeather()
      weatherData.value = weather
    } catch (err) {
      weatherError.value = 'No se pudo obtener el clima'
      console.warn('Weather error:', err)
    }
  } catch (err) {
    connectionStatus.value = 'Sin conexión'
    errorMessage.value = 'No se puede conectar con el backend. ¿Está corriendo uvicorn?'
    console.error('Init error:', err)
  }
}

// ============================================================
// Lifecycle
// ============================================================

onMounted(() => {
  loadInitialData()
})
</script>

<style scoped>
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-green-400);
  animation: pulseGlow 2s infinite;
}

/* Error Toast */
.error-toast {
  position: fixed;
  bottom: var(--space-lg);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--color-red-400);
  font-size: var(--font-size-sm);
  cursor: pointer;
  z-index: 1000;
}

.toast-close {
  opacity: 0.5;
  margin-left: var(--space-sm);
}

/* Toast transition */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
