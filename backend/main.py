"""
API REST del Simulador de Invernadero.

Endpoints:
    GET  /api/materials          → Lista de materiales disponibles
    POST /api/simulate           → Simulación térmica para un material
    POST /api/simulate/compare   → Simulación comparativa de múltiples materiales
    POST /api/laplace            → Análisis de función de transferencia (Laplace)
    GET  /api/weather            → Datos climáticos actuales (OpenWeatherMap)
    GET  /api/geocode            → Búsqueda de ciudades (geocoding)

Servidor: uvicorn main:app --reload --port 8000
Docs interactiva: http://localhost:8000/docs
"""

import os
import logging

import httpx

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from engine.materials import (
    MATERIALES,
    calcular_k,
    calcular_area_cubierta,
    calcular_volumen,
    obtener_materiales_lista,
    obtener_transmitancia_solar,
)
from engine.thermal_engine import ThermalEngine
from engine.climate_model import (
    obtener_clima_openweather,
    obtener_clima_actual,
    interpolar_temperatura,
    generar_datos_simulacion,
)
from models.schemas import (
    SimulationRequest,
    SimulationResponse,
    CompareRequest,
    CompareResponse,
    LaplaceRequest,
    LaplaceResponse,
    WeatherResponse,
)

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", "19.2510"))
DEFAULT_LON = float(os.getenv("DEFAULT_LON", "-97.8948"))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# Crear aplicación FastAPI
# ============================================================

app = FastAPI(
    title="Simulador de Invernadero API",
    description=(
        "API para simulación térmica de invernaderos. "
        "Usa la Ley de Enfriamiento de Newton con Método de Euler Mejorado "
        "y análisis de Laplace para funciones de transferencia."
    ),
    version="1.0.0",
)

# CORS para desarrollo local (Vue en puerto 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Endpoints
# ============================================================

@app.get("/api/materials")
async def listar_materiales():
    """
    Lista todos los materiales de cubierta disponibles con sus propiedades.
    """
    return obtener_materiales_lista()


@app.post("/api/simulate", response_model=SimulationResponse)
async def simular(req: SimulationRequest):
    """
    Ejecuta una simulación térmica de invernadero para un material.
    
    Recibe los parámetros de la simulación y retorna los arrays de
    temperatura interior/exterior y radiación para cada minuto.
    """
    # Validar material
    if req.material_id not in MATERIALES:
        raise HTTPException(
            status_code=400,
            detail=f"Material '{req.material_id}' no encontrado. "
                   f"Materiales disponibles: {list(MATERIALES.keys())}",
        )

    # Calcular dimensiones y constante k
    area = calcular_area_cubierta(req.largo, req.ancho, req.alto)
    volumen = calcular_volumen(req.largo, req.ancho, req.alto)
    k = calcular_k(req.material_id, area, volumen)
    alpha_solar = obtener_transmitancia_solar(req.material_id)

    n_minutos = req.horas * 60

    # Obtener datos climáticos
    T_ext, rad = await _obtener_datos_climaticos(
        req.usar_api_clima, n_minutos, req.T_min_fallback, req.T_max_fallback,
        lat=req.lat, lon=req.lon,
    )

    # Factor alpha ajustado: la radiación que pasa se convierte en calor interior
    # alpha = transmitancia_solar × factor_de_conversión
    alpha_factor = alpha_solar * 0.006  # Factor empírico: W/m² → °C/min

    # Ejecutar simulación
    engine = ThermalEngine(k=k, alpha=alpha_factor)
    resultado = engine.simular(T0=req.T_inicial, T_ext_array=T_ext, rad_array=rad)

    mat_info = MATERIALES[req.material_id]
    return SimulationResponse(
        material_id=req.material_id,
        material_nombre=mat_info["nombre"],
        color=mat_info["color"],
        tiempo_horas=resultado["tiempo_horas"],
        T_interior=resultado["T_interior"],
        T_exterior=resultado["T_exterior"],
        radiacion=resultado["radiacion"],
        T_max_int=resultado["T_max_int"],
        T_min_int=resultado["T_min_int"],
        T_promedio_int=resultado["T_promedio_int"],
        k_utilizado=round(k, 6),
    )


@app.post("/api/simulate/compare", response_model=CompareResponse)
async def simular_comparacion(req: CompareRequest):
    """
    Ejecuta simulaciones térmicas comparativas para múltiples materiales.
    
    Todos los materiales se simulan con las mismas condiciones climáticas
    para una comparación justa.
    """
    # Validar materiales
    for mat_id in req.material_ids:
        if mat_id not in MATERIALES:
            raise HTTPException(
                status_code=400,
                detail=f"Material '{mat_id}' no encontrado.",
            )

    n_minutos = req.horas * 60
    area = calcular_area_cubierta(req.largo, req.ancho, req.alto)
    volumen = calcular_volumen(req.largo, req.ancho, req.alto)

    # Obtener datos climáticos (una sola vez para todos)
    T_ext, rad = await _obtener_datos_climaticos(
        req.usar_api_clima, n_minutos, req.T_min_fallback, req.T_max_fallback,
        lat=req.lat, lon=req.lon,
    )

    simulaciones = []
    for mat_id in req.material_ids:
        k = calcular_k(mat_id, area, volumen)
        alpha_solar = obtener_transmitancia_solar(mat_id)
        alpha_factor = alpha_solar * 0.006

        engine = ThermalEngine(k=k, alpha=alpha_factor)
        resultado = engine.simular(T0=req.T_inicial, T_ext_array=T_ext, rad_array=rad)

        mat_info = MATERIALES[mat_id]
        simulaciones.append(SimulationResponse(
            material_id=mat_id,
            material_nombre=mat_info["nombre"],
            color=mat_info["color"],
            tiempo_horas=resultado["tiempo_horas"],
            T_interior=resultado["T_interior"],
            T_exterior=resultado["T_exterior"],
            radiacion=resultado["radiacion"],
            T_max_int=resultado["T_max_int"],
            T_min_int=resultado["T_min_int"],
            T_promedio_int=resultado["T_promedio_int"],
            k_utilizado=round(k, 6),
        ))

    # Usar los datos comunes del primer resultado
    return CompareResponse(
        simulaciones=simulaciones,
        tiempo_horas=simulaciones[0].tiempo_horas,
        T_exterior=simulaciones[0].T_exterior,
        radiacion=simulaciones[0].radiacion,
    )


@app.post("/api/laplace", response_model=LaplaceResponse)
async def analisis_laplace(req: LaplaceRequest):
    """
    Realiza el análisis de Laplace del invernadero para un material dado.
    
    Calcula la función de transferencia H(s) = k/(s+k), la constante de tiempo τ,
    el polo del sistema, y genera la respuesta al escalón unitario.
    """
    if req.material_id not in MATERIALES:
        raise HTTPException(
            status_code=400,
            detail=f"Material '{req.material_id}' no encontrado.",
        )

    area = calcular_area_cubierta(req.largo, req.ancho, req.alto)
    volumen = calcular_volumen(req.largo, req.ancho, req.alto)
    k = calcular_k(req.material_id, area, volumen)

    engine = ThermalEngine(k=k)
    analisis = engine.laplace_analysis()

    mat_info = MATERIALES[req.material_id]
    return LaplaceResponse(
        material_id=req.material_id,
        material_nombre=mat_info["nombre"],
        k_utilizado=round(k, 6),
        **analisis,
    )


@app.get("/api/weather", response_model=WeatherResponse)
async def clima_actual(
    lat: float = DEFAULT_LAT,
    lon: float = DEFAULT_LON,
):
    """
    Obtiene los datos climáticos actuales desde OpenWeatherMap.
    """
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key de OpenWeatherMap no configurada.",
        )

    try:
        datos = await obtener_clima_actual(lat, lon, API_KEY)
        return WeatherResponse(**datos)
    except Exception as e:
        logger.error(f"Error al obtener clima: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Error al conectar con OpenWeatherMap: {str(e)}",
        )


@app.get("/api/geocode")
async def buscar_ciudades(q: str = "", limit: int = 5):
    """
    Busca ciudades usando la API de geocoding de OpenWeatherMap.
    Retorna una lista de coincidencias con nombre, país, lat y lon.
    """
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key de OpenWeatherMap no configurada.",
        )
    if not q or len(q.strip()) < 2:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "http://api.openweathermap.org/geo/1.0/direct",
                params={"q": q, "limit": limit, "appid": API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data:
            results.append({
                "name": item.get("name", ""),
                "country": item.get("country", ""),
                "state": item.get("state", ""),
                "lat": item.get("lat"),
                "lon": item.get("lon"),
            })
        return results
    except Exception as e:
        logger.error(f"Error en geocoding: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Error al buscar ciudades: {str(e)}",
        )


# ============================================================
# Utilidades internas
# ============================================================

async def _obtener_datos_climaticos(
    usar_api: bool,
    n_minutos: int,
    T_min: float,
    T_max: float,
    lat: float | None = None,
    lon: float | None = None,
) -> tuple:
    """
    Obtiene datos de temperatura exterior y radiación solar.
    Intenta usar la API de OpenWeatherMap; si falla, usa el fallback.
    """
    T_ext = None
    nubosidad = 0.0
    use_lat = lat if lat is not None else DEFAULT_LAT
    use_lon = lon if lon is not None else DEFAULT_LON

    if usar_api and API_KEY:
        try:
            datos_api = await obtener_clima_openweather(use_lat, use_lon, API_KEY)
            T_ext_3h = datos_api["temperaturas"]
            nubosidad = datos_api.get("nubosidad", [0])[0] if datos_api.get("nubosidad") else 0
            T_ext_interpolada = interpolar_temperatura(T_ext_3h, n_minutos)
            T_ext = T_ext_interpolada
            logger.info(f"Datos climáticos obtenidos de OpenWeatherMap: {len(T_ext_3h)} puntos")
        except Exception as e:
            logger.warning(f"OpenWeatherMap no disponible, usando fallback: {e}")

    return generar_datos_simulacion(
        temperaturas_ext=T_ext,
        usar_fallback=(T_ext is None),
        n_minutos=n_minutos,
        T_min=T_min,
        T_max=T_max,
        nubosidad=nubosidad,
    )


# ============================================================
# Punto de entrada
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
