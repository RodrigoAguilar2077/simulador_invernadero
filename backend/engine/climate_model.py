"""
Modelo climático para el simulador de invernadero

"""

import math
import numpy as np
from scipy.interpolate import CubicSpline
import httpx
from datetime import datetime, timezone


# Integración con OpenWeatherMap API

async def obtener_clima_openweather(
    lat: float,
    lon: float,
    api_key: str,
) -> dict:
    """
    Obtiene el pronóstico del clima desde OpenWeatherMap
    
    Endpoint: https://api.openweathermap.org/data/2.5/forecast
    
    Args:
        lat: Latitud en grados decimales
        lon: Longitud en grados decimales
        api_key: API key de OpenWeatherMap
    
    Returns:
        Diccionario con:
            - temperaturas: Lista de temperaturas [°C] cada 3 horas
            - timestamps: Lista de timestamps Unix
            - humedad: Lista de humedad relativa [%]
            - nubosidad: Lista de cobertura de nubes [%]
            - descripcion: Descripción del clima actual
            - ciudad: Nombre de la ciudad detectada
    
    Raises:
        httpx.HTTPError: Si la llamada a la API falla
    """
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",    # Temperatura en °C
        "lang": "es",         # Descripciones en español
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    # Extraer datos de los primeros 8 puntos (24 horas) + 1 extra para interpolación
    n_puntos = min(len(data["list"]), 9)
    puntos = data["list"][:n_puntos]

    temperaturas = [p["main"]["temp"] for p in puntos]
    timestamps = [p["dt"] for p in puntos]
    humedad = [p["main"]["humidity"] for p in puntos]
    nubosidad = [p["clouds"]["all"] for p in puntos]

    # Datos del clima actual (primer punto)
    clima_actual = puntos[0]
    descripcion = clima_actual["weather"][0]["description"]
    ciudad = data.get("city", {}).get("name", "Desconocido")

    return {
        "temperaturas": temperaturas,
        "timestamps": timestamps,
        "humedad": humedad,
        "nubosidad": nubosidad,
        "descripcion": descripcion,
        "ciudad": ciudad,
        "temp_actual": temperaturas[0],
        "humedad_actual": humedad[0],
    }


async def obtener_clima_actual(lat: float, lon: float, api_key: str) -> dict:
    """
    Obtiene el clima actual desde OpenWeatherMap (Current Weather endpoint).
    
    Args:
        lat: Latitud en grados decimales
        lon: Longitud en grados decimales
        api_key: API key de OpenWeatherMap
    
    Returns:
        Diccionario con datos del clima actual
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "es",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return {
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "temp_min": data["main"]["temp_min"],
        "temp_max": data["main"]["temp_max"],
        "humedad": data["main"]["humidity"],
        "presion": data["main"]["pressure"],
        "nubosidad": data["clouds"]["all"],
        "descripcion": data["weather"][0]["description"],
        "icono": data["weather"][0]["icon"],
        "viento_velocidad": data["wind"]["speed"],
        "ciudad": data.get("name", "Desconocido"),
        "amanecer": data["sys"].get("sunrise"),
        "atardecer": data["sys"].get("sunset"),
    }


# Interpolación de datos climáticos

def interpolar_temperatura(
    temperaturas_3h: list[float],
    n_minutos: int = 1440,
) -> np.ndarray:
    """
    Interpola temperaturas de intervalos de 3 horas a intervalos de 1 minuto
    usando Spline Cúbica para una curva suave y natural.
    
    Args:
        temperaturas_3h: Lista de temperaturas cada 3 horas [°C]
        n_minutos: Número total de minutos a generar (default: 1440 = 24h)
    
    Returns:
        Array NumPy de temperaturas interpoladas, un valor por minuto [°C]
    """
    n_puntos = len(temperaturas_3h)
    # Puntos originales en minutos 
    x_original = np.arange(n_puntos) * 180.0
    y_original = np.array(temperaturas_3h)

    # Crear spline cúbica
    cs = CubicSpline(x_original, y_original, bc_type="natural")

    # Interpolar a cada minuto
    x_interpolado = np.arange(n_minutos, dtype=float)
    
    # Limitar al rango de datos disponibles
    x_max = x_original[-1]
    # Para minutos más allá de los datos, usar el último valor conocido
    y_interpolado = np.zeros(n_minutos)
    mask_dentro = x_interpolado <= x_max
    y_interpolado[mask_dentro] = cs(x_interpolado[mask_dentro])
    y_interpolado[~mask_dentro] = y_original[-1]

    return y_interpolado


# Modelo de radiación solar

def modelo_radiacion_solar(
    n_minutos: int = 1440,
    R_max: float = 850.0,
    hora_amanecer: float = 6.5,
    hora_atardecer: float = 18.5,
    nubosidad_pct: float = 0.0,
) -> np.ndarray:
    """
    Genera un perfil de radiación solar diaria usando un modelo sinusoidal truncado.
    
    La radiación solar se modela como una onda sinusoidal que es cero antes del
    amanecer y después del atardecer:
    
        R(t) = R_max × sin(π × (t - t_amanecer) / (t_atardecer - t_amanecer))
        
    Para horas fuera del rango [amanecer, atardecer], R(t) = 0.
    
    La nubosidad reduce la radiación proporcionalmente.
    
    Args:
        n_minutos: Número total de minutos (default: 1440 = 24h)
        R_max: Radiación solar máxima al mediodía [W/m²]
        hora_amanecer: Hora del amanecer (decimal, ej. 6.5 = 6:30am)
        hora_atardecer: Hora del atardecer (decimal, ej. 18.5 = 6:30pm)
        nubosidad_pct: Porcentaje de nubosidad [0-100]. Reduce la radiación.
    
    Returns:
        Array NumPy de radiación solar, un valor por minuto [W/m²]
    """
    radiacion = np.zeros(n_minutos)
    duracion_luz = hora_atardecer - hora_amanecer

    # Factor de reducción por nubosidad 
    factor_nubes = 1.0 - (nubosidad_pct / 100.0) * 0.75

    for minuto in range(n_minutos):
        hora = minuto / 60.0
        if hora_amanecer <= hora <= hora_atardecer:
            # Onda sinusoidal en el periodo de luz
            fase = math.pi * (hora - hora_amanecer) / duracion_luz
            radiacion[minuto] = R_max * math.sin(fase) * factor_nubes

    return radiacion


# Modelo climático fallback (sin API)

def clima_fallback_tlaxcala(
    n_minutos: int = 1440,
    T_min: float = 4.0,
    T_max: float = 22.0,
    hora_T_min: float = 6.0,
) -> np.ndarray:
    """
    Modelo sinusoidal de temperatura diurna para la región de Tlaxcala.
    
    Genera un perfil de temperatura de 24 horas basado en una función
    sinusoidal calibrada con las temperaturas típicas de la zona.
    
    La temperatura mínima ocurre alrededor de las 6:00 am y la máxima
    alrededor de las 14:00 (2:00 pm).
    
    T(t) = T_media + A × sin(2π × (t - 8) / 24)
    
    Args:
        n_minutos: Número total de minutos (default: 1440 = 24h)
        T_min: Temperatura mínima del día [°C]
        T_max: Temperatura máxima del día [°C]
        hora_T_min: Hora a la que ocurre la temperatura mínima
    
    Returns:
        Array NumPy de temperaturas, un valor por minuto [°C]
    """
    T_media = (T_min + T_max) / 2.0
    amplitud = (T_max - T_min) / 2.0

    temperaturas = np.zeros(n_minutos)
    for minuto in range(n_minutos):
        hora = minuto / 60.0
        # Fase ajustada para que el mínimo sea a las ~6am
        temperaturas[minuto] = T_media + amplitud * math.sin(
            2 * math.pi * (hora - hora_T_min - 6) / 24.0
        )

    return temperaturas


def generar_datos_simulacion(
    temperaturas_ext: np.ndarray | None = None,
    usar_fallback: bool = False,
    n_minutos: int = 1440,
    T_min: float = 4.0,
    T_max: float = 22.0,
    nubosidad: float = 0.0,
    R_max: float = 850.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Genera los arrays de temperatura exterior y radiación solar
    listos para la simulación.
    
    Args:
        temperaturas_ext: Array de T_ext ya interpoladas (si viene de API)
        usar_fallback: Si True, usa el modelo sinusoidal local
        n_minutos: Duración de la simulación en minutos
        T_min, T_max: Temperaturas para el modelo fallback
        nubosidad: Porcentaje de nubosidad
        R_max: Radiación solar máxima
    
    Returns:
        Tupla (T_ext_array, rad_array), ambos de tamaño n_minutos
    """
    if temperaturas_ext is not None and not usar_fallback:
        T_ext = temperaturas_ext[:n_minutos]
        # Si no tenemos suficientes datos, rellenar con el último valor
        if len(T_ext) < n_minutos:
            padding = np.full(n_minutos - len(T_ext), T_ext[-1])
            T_ext = np.concatenate([T_ext, padding])
    else:
        T_ext = clima_fallback_tlaxcala(n_minutos, T_min, T_max)

    rad = modelo_radiacion_solar(n_minutos, R_max=R_max, nubosidad_pct=nubosidad)

    return T_ext, rad
