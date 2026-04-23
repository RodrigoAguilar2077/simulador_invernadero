"""
Modelos Pydantic para validación de requests y responses de la API.

Define las estructuras de datos que viajan entre el frontend y el backend,
con validación automática de tipos y rangos.
"""

from pydantic import BaseModel, Field


# ============================================================
# Request Models
# ============================================================

class SimulationRequest(BaseModel):
    """Parámetros para ejecutar una simulación térmica."""
    material_id: str = Field(
        ...,
        description="ID del material de la cubierta",
        examples=["vidrio_simple", "polietileno_ldpe"],
    )
    T_inicial: float = Field(
        default=15.0,
        ge=-20, le=60,
        description="Temperatura interior inicial [°C]",
    )
    horas: int = Field(
        default=24,
        ge=1, le=72,
        description="Duración de la simulación [horas]",
    )
    largo: float = Field(
        default=10.0,
        gt=0, le=100,
        description="Largo del invernadero [m]",
    )
    ancho: float = Field(
        default=5.0,
        gt=0, le=50,
        description="Ancho del invernadero [m]",
    )
    alto: float = Field(
        default=3.0,
        gt=0, le=15,
        description="Alto del invernadero [m]",
    )
    usar_api_clima: bool = Field(
        default=True,
        description="Si True, usa datos reales de OpenWeatherMap. Si False, usa modelo sinusoidal.",
    )
    T_min_fallback: float = Field(
        default=4.0,
        ge=-20, le=40,
        description="Temperatura mínima para el modelo fallback [°C]",
    )
    T_max_fallback: float = Field(
        default=22.0,
        ge=-10, le=50,
        description="Temperatura máxima para el modelo fallback [°C]",
    )
    lat: float | None = Field(
        default=None,
        description="Latitud de la ubicación (para clima dinámico)",
    )
    lon: float | None = Field(
        default=None,
        description="Longitud de la ubicación (para clima dinámico)",
    )


class CompareRequest(BaseModel):
    """Parámetros para simulación comparativa de múltiples materiales."""
    material_ids: list[str] = Field(
        ...,
        min_length=1,
        max_length=6,
        description="Lista de IDs de materiales a comparar",
    )
    T_inicial: float = Field(default=15.0, ge=-20, le=60)
    horas: int = Field(default=24, ge=1, le=72)
    largo: float = Field(default=10.0, gt=0, le=100)
    ancho: float = Field(default=5.0, gt=0, le=50)
    alto: float = Field(default=3.0, gt=0, le=15)
    usar_api_clima: bool = Field(default=True)
    T_min_fallback: float = Field(default=4.0, ge=-20, le=40)
    T_max_fallback: float = Field(default=22.0, ge=-10, le=50)
    lat: float | None = Field(default=None)
    lon: float | None = Field(default=None)


class LaplaceRequest(BaseModel):
    """Parámetros para el análisis de Laplace."""
    material_id: str = Field(
        ...,
        description="ID del material a analizar",
    )
    largo: float = Field(default=10.0, gt=0, le=100)
    ancho: float = Field(default=5.0, gt=0, le=50)
    alto: float = Field(default=3.0, gt=0, le=15)


# ============================================================
# Response Models
# ============================================================

class MaterialInfo(BaseModel):
    """Información de un material para el frontend."""
    id: str
    nombre: str
    descripcion: str
    # Usamos alias para el campo lambda (palabra reservada en Python)
    lambda_val: float = Field(..., alias="lambda")
    U: float
    espesor_mm: float
    transmitancia_solar: float
    color: str
    icono: str

    class Config:
        populate_by_name = True


class SimulationResponse(BaseModel):
    """Resultados de una simulación térmica."""
    material_id: str
    material_nombre: str
    color: str
    tiempo_horas: list[float]
    T_interior: list[float]
    T_exterior: list[float]
    radiacion: list[float]
    T_max_int: float
    T_min_int: float
    T_promedio_int: float
    k_utilizado: float


class CompareResponse(BaseModel):
    """Resultados de simulación comparativa."""
    simulaciones: list[SimulationResponse]
    tiempo_horas: list[float]
    T_exterior: list[float]
    radiacion: list[float]


class LaplaceResponse(BaseModel):
    """Resultados del análisis de Laplace."""
    material_id: str
    material_nombre: str
    tau_minutos: float
    tau_horas: float
    polo: float
    ganancia_estatica: float
    tiempo_estabilizacion_min: float
    tiempo_estabilizacion_horas: float
    clasificacion: str
    descripcion: str
    step_response_t: list[float]
    step_response_y: list[float]
    k_utilizado: float


class WeatherResponse(BaseModel):
    """Datos del clima actual."""
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    humedad: int
    presion: int
    nubosidad: int
    descripcion: str
    icono: str
    viento_velocidad: float
    ciudad: str
    amanecer: int | None = None
    atardecer: int | None = None


class ErrorResponse(BaseModel):
    """Respuesta de error estándar."""
    detail: str
    code: str = "error"
