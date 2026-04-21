/**
 * Service layer para comunicarse con el backend FastAPI.
 * Base URL: http://localhost:8000/api
 */

const BASE_URL = 'http://localhost:8000/api'

/**
 * Wrapper genérico para peticiones fetch con manejo de errores.
 */
async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  }

  try {
    const response = await fetch(url, config)
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error desconocido' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }
    return await response.json()
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('No se puede conectar con el servidor. ¿Está corriendo el backend?')
    }
    throw err
  }
}

/**
 * Obtiene la lista de materiales disponibles.
 * @returns {Promise<Array>} Lista de materiales con sus propiedades
 */
export async function fetchMaterials() {
  return request('/materials')
}

/**
 * Ejecuta una simulación térmica para un solo material.
 * @param {Object} params - Parámetros de simulación
 * @returns {Promise<Object>} Resultados de la simulación
 */
export async function runSimulation(params) {
  return request('/simulate', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

/**
 * Ejecuta simulaciones comparativas de múltiples materiales.
 * @param {Object} params - Parámetros incluyendo material_ids[]
 * @returns {Promise<Object>} Resultados comparativos
 */
export async function compareSimulation(params) {
  return request('/simulate/compare', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

/**
 * Obtiene el análisis de Laplace para un material.
 * @param {Object} params - material_id, dimensiones
 * @returns {Promise<Object>} Análisis de función de transferencia
 */
export async function fetchLaplaceAnalysis(params) {
  return request('/laplace', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

/**
 * Obtiene datos climáticos actuales de OpenWeatherMap.
 * @param {number} lat - Latitud
 * @param {number} lon - Longitud
 * @returns {Promise<Object>} Datos del clima actual
 */
export async function fetchWeather(lat = 19.2510, lon = -97.8948) {
  return request(`/weather?lat=${lat}&lon=${lon}`)
}
