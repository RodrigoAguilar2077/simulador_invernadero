<template>
  <div class="location-search">
    <h3 class="section-title">
      <span class="section-title__icon"><MapPin size="20" /></span>
      Ubicación
    </h3>
    <div class="search-wrapper">
      <input
        type="text"
        class="search-input"
        placeholder="Buscar ciudad..."
        v-model="query"
        @input="onInput"
        @focus="showResults = true"
      />
      <div class="search-icon"><Search size="16" /></div>
    </div>

    <div v-if="showResults && results.length > 0" class="search-results">
      <div
        v-for="(city, i) in results"
        :key="i"
        class="search-result-item"
        @click="selectCity(city)"
      >
        <span class="search-result-name">{{ city.name }}</span>
        <span class="search-result-meta">
          {{ city.state ? city.state + ', ' : '' }}{{ city.country }}
        </span>
      </div>
    </div>

    <div v-if="selectedCity" class="selected-city fade-in">
      <span class="selected-city__pin"><MapPin size="14" /></span>
      <span class="selected-city__name">{{ selectedCity.name }}</span>
      <span class="selected-city__country">{{ selectedCity.country }}</span>
      <span class="selected-city__coords">
        {{ selectedCity.lat.toFixed(2) }}°, {{ selectedCity.lon.toFixed(2) }}°
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { searchCities } from '../services/api.js'
import { MapPin, Search } from 'lucide-vue-next'

const emit = defineEmits(['city-selected'])

const query = ref('')
const results = ref([])
const showResults = ref(false)
const selectedCity = ref(null)
let debounceTimer = null

function onInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (query.value.trim().length < 2) {
      results.value = []
      return
    }
    try {
      results.value = await searchCities(query.value)
    } catch (e) {
      console.warn('Geocoding error:', e)
      results.value = []
    }
  }, 350)
}

function selectCity(city) {
  selectedCity.value = city
  query.value = city.name
  showResults.value = false
  results.value = []
  emit('city-selected', { lat: city.lat, lon: city.lon, name: city.name, country: city.country })
}
</script>

<style scoped>
.location-search { position: relative; }
.search-wrapper { position: relative; margin-bottom: var(--space-sm); }
.search-input {
  width: 100%; padding: var(--space-sm) var(--space-md);
  padding-right: 36px;
  background: var(--color-bg-surface); border: 1px solid var(--glass-border);
  border-radius: var(--radius-md); color: var(--color-text-primary);
  font-family: var(--font-family); font-size: var(--font-size-sm);
  outline: none; transition: border-color var(--transition-base);
}
.search-input:focus { border-color: var(--color-purple-400); }
.search-input::placeholder { color: var(--color-text-muted); }
.search-icon {
  position: absolute; right: var(--space-sm); top: 50%; transform: translateY(-50%);
  font-size: var(--font-size-sm); pointer-events: none;
}
.search-results {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 9999;
  background: var(--color-bg-elevated); border: 1px solid var(--glass-border);
  border-radius: var(--radius-md); overflow: hidden;
  box-shadow: var(--shadow-lg);
}
.search-result-item {
  padding: var(--space-sm) var(--space-md);
  cursor: pointer; display: flex; justify-content: space-between; align-items: center;
  transition: background var(--transition-fast);
  font-size: var(--font-size-sm);
}
.search-result-item:hover { background: rgba(192,132,252,0.08); }
.search-result-name { color: var(--color-text-primary); font-weight: 500; }
.search-result-meta { color: var(--color-text-muted); font-size: var(--font-size-xs); }
.selected-city {
  display: flex; align-items: center; gap: var(--space-xs);
  padding: var(--space-sm); background: rgba(192,132,252,0.06);
  border: 1px solid rgba(192,132,252,0.15); border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}
.selected-city__name { color: var(--color-purple-400); font-weight: 600; }
.selected-city__country { color: var(--color-text-muted); }
.selected-city__coords { margin-left: auto; color: var(--color-text-muted); font-variant-numeric: tabular-nums; }
</style>
