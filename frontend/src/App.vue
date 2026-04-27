<template>
  <div id="app-root" :style="appStyle">
    <!-- MAIN CONTENT -->
    <div class="main-content">
      <!-- TOP HEADER -->
      <header class="top-header">
        <div class="top-header__left">
          <div class="top-header__badge">
            <span class="badge-dot"></span>
            {{ connectionStatus }}
          </div>
          <WeatherInfo :weather="weatherData" :error="weatherError" compact />
        </div>
      </header>

      <!-- SECTION 1: EL SABER -->
      <section class="spa-section" id="section-intro">
        <HeroSection @scroll-to-simulator="scrollTo('section-simulator')" />
      </section>

      <!-- SECTION 2: EL CONFIGURADOR + SIMULADOR -->
      <section class="spa-section" id="section-simulator">
        <h2 class="section-heading">Simulador Térmico</h2>
        <div class="simulator-grid">
          <!-- LEFT: Config Panel -->
          <aside class="simulator-sidebar">
            <div class="glass-card sidebar-panel sidebar-panel--overflow">
              <LocationSearch @city-selected="onCitySelected" />
            </div>
            <div class="glass-card sidebar-panel">
              <MaterialSelector
                :materials="materials"
                :selectedMaterials="selectedMaterials"
                :dimensions="dimensions"
                :loading="simulating"
                @toggle-material="toggleMaterial"
                @simulate="runSimulation"
              />
            </div>
          </aside>

          <!-- RIGHT: Results -->
          <div class="simulator-results">
            <div class="glass-card">
              <TemperatureChart :simulationData="simulationResult" />
            </div>

            <EfficiencyCards
              :simulationData="simulationResult"
              :loading="simulating"
            />
          </div>
        </div>
      </section>

      <!-- SECTION 3: MODO INGENIERO -->
      <section class="spa-section" id="section-engineer">
        <EngineerMode :laplaceData="laplaceData" />
      </section>
    </div>

    <!-- Error Toast -->
    <Transition name="toast">
      <div v-if="errorMessage" class="error-toast glass-card" @click="errorMessage = ''">
        <span>{{ errorMessage }}</span>
        <span class="toast-close">✕</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import HeroSection from './components/HeroSection.vue'
import LocationSearch from './components/LocationSearch.vue'
import MaterialSelector from './components/MaterialSelector.vue'
import TemperatureChart from './components/TemperatureChart.vue'
import WeatherInfo from './components/WeatherInfo.vue'
import EfficiencyCards from './components/EfficiencyCards.vue'
import EngineerMode from './components/EngineerMode.vue'
import {
  fetchMaterials,
  compareSimulation,
  fetchLaplaceAnalysis,
  fetchWeather,
} from './services/api.js'


// State


const materials = ref([])
const selectedMaterials = ref([])
const simulating = ref(false)
const simulationResult = ref(null)
const laplaceData = ref(null)
const weatherData = ref(null)
const weatherError = ref('')
const errorMessage = ref('')
const connectionStatus = ref('Conectando...')

const appStyle = computed(() => {
  const baseTemp = weatherData.value ? weatherData.value.temp : 20;
  
  const minT = 0;
  const maxT = 40;
  let factor = (baseTemp - minT) / (maxT - minT);
  factor = Math.max(0, Math.min(1, factor));

  // Adjusted for dark mode: deeper colors that blend well
  const colorFrio = {r: 59, g: 130, b: 246}; // Blue
  const colorCalor = {r: 251, g: 146, b: 60}; // Orange

  const r = Math.round(colorFrio.r + (colorCalor.r - colorFrio.r) * factor);
  const g = Math.round(colorFrio.g + (colorCalor.g - colorFrio.g) * factor);
  const b = Math.round(colorFrio.b + (colorCalor.b - colorFrio.b) * factor);

  return {
    background: `linear-gradient(to bottom, rgba(${r}, ${g}, ${b}, 0.15) 0%, var(--color-bg-deep) 40%)`
  }
})

const selectedCoords = reactive({ lat: 19.2510, lon: -97.8948 })

const dimensions = reactive({
  largo: 10,
  ancho: 5,
  alto: 3,
  T_inicial: 15,
  horas: 24,
})

onMounted(() => {
  loadInitialData()
})

// Methods


function scrollTo(id) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function onCitySelected({ lat, lon }) {
  selectedCoords.lat = lat
  selectedCoords.lon = lon

  loadWeather(lat, lon)
}

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
    const result = await compareSimulation({
      material_ids: selectedMaterials.value,
      T_inicial: dimensions.T_inicial,
      horas: dimensions.horas,
      largo: dimensions.largo,
      ancho: dimensions.ancho,
      alto: dimensions.alto,
      usar_api_clima: true,
      lat: selectedCoords.lat,
      lon: selectedCoords.lon,
    })
    simulationResult.value = result

    // Also run Laplace analysis for first selected material
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

async function loadWeather(lat, lon) {
  try {
    const weather = await fetchWeather(lat, lon)
    weatherData.value = weather
  } catch (err) {
    weatherError.value = 'No se pudo obtener el clima'
    console.warn('Weather error:', err)
  }
}

async function loadInitialData() {
  try {
    const mats = await fetchMaterials()
    materials.value = mats
    connectionStatus.value = 'API Conectada'

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          selectedCoords.lat = position.coords.latitude
          selectedCoords.lon = position.coords.longitude
          await loadWeather(selectedCoords.lat, selectedCoords.lon)
        },
        async (error) => {
          console.warn('Geolocation error or denied:', error)
          await loadWeather(selectedCoords.lat, selectedCoords.lon)
        }
      )
    } else {
      await loadWeather(selectedCoords.lat, selectedCoords.lon)
    }
  } catch (err) {
    connectionStatus.value = 'Sin conexión'
    errorMessage.value = 'No se puede conectar con el backend. ¿Está corriendo uvicorn?'
    console.error('Init error:', err)
  }
}
</script>

<style scoped>
.sidebar-panel { padding: var(--space-lg); }
.sidebar-panel + .sidebar-panel { margin-top: var(--space-md); }
.sidebar-panel--overflow { overflow: visible; position: relative; z-index: 10; }

.simulator-sidebar {
  display: flex; flex-direction: column; gap: 0;
  position: sticky; top: 60px; align-self: start;
}

.simulator-results {
  display: flex; flex-direction: column; gap: var(--space-lg);
  min-width: 0;
}

/* Error Toast */
.error-toast {
  position: fixed; bottom: var(--space-lg); left: 50%;
  transform: translateX(-50%);
  display: flex; align-items: center; gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  background: rgba(239,68,68,0.15);
  border: 1px solid rgba(239,68,68,0.3);
  color: var(--color-red-400);
  font-size: var(--font-size-sm);
  cursor: pointer; z-index: 1000;
}
.toast-close { opacity: 0.5; margin-left: var(--space-sm); }
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(20px); }

#app-root {
  flex: 1;
  width: 100%;
  min-height: 100vh;
  transition: background 1s ease-in-out;
}

@media (max-width: 768px) {
  .simulator-sidebar {
    position: static;
  }
}
</style>
