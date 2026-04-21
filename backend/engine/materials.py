"""
Catálogo de materiales para cubiertas de invernadero.

Valores de conductividad térmica (λ) y transmitancia térmica (U)
tomados de tablas de referencia de ingeniería agrícola.

La constante k del modelo se calcula dinámicamente a partir de U,
las dimensiones del invernadero, y las propiedades del aire interior.
"""

# Propiedades del aire a ~20°C
RHO_AIRE = 1.2041       # kg/m³ — densidad del aire
CP_AIRE = 1005.0         # J/(kg·K) — calor específico del aire

# Catálogo de materiales con valores tabulados
MATERIALES = {
    "vidrio_simple": {
        "nombre": "Vidrio Simple (4mm)",
        "descripcion": "Vidrio flotado estándar de 4mm. Alta transmisión de luz pero baja retención térmica nocturna.",
        "lambda_W_mK": 1.00,       # Conductividad térmica [W/(m·K)]
        "espesor_mm": 4,
        "U_W_m2K": 5.8,            # Transmitancia térmica global [W/(m²·K)]
        "transmitancia_solar": 0.85, # Fracción de radiación solar que pasa
        "color": "#88c0d0",         # Color para la gráfica
        "icono": "🪟",
    },
    "vidrio_doble": {
        "nombre": "Vidrio Doble (4+4mm)",
        "descripcion": "Doble acristalamiento con cámara de aire. Mejor aislamiento que vidrio simple.",
        "lambda_W_mK": 1.00,
        "espesor_mm": 8,
        "U_W_m2K": 3.0,
        "transmitancia_solar": 0.75,
        "color": "#5e81ac",
        "icono": "🏠",
    },
    "polietileno_ldpe": {
        "nombre": "Polietileno LDPE (200μm)",
        "descripcion": "Film plástico económico y ligero. Muy común en invernaderos de bajo costo.",
        "lambda_W_mK": 0.33,
        "espesor_mm": 0.2,
        "U_W_m2K": 6.5,
        "transmitancia_solar": 0.88,
        "color": "#a3be8c",
        "icono": "🛡️",
    },
    "polietileno_doble": {
        "nombre": "Polietileno Doble Capa",
        "descripcion": "Doble capa de polietileno inflada con aire. Mejora significativa en aislamiento.",
        "lambda_W_mK": 0.33,
        "espesor_mm": 0.4,
        "U_W_m2K": 4.0,
        "transmitancia_solar": 0.78,
        "color": "#8fbcbb",
        "icono": "🔰",
    },
    "policarbonato_6mm": {
        "nombre": "Policarbonato Alveolar (6mm)",
        "descripcion": "Placa alveolar de policarbonato. Excelente relación aislamiento/peso.",
        "lambda_W_mK": 0.20,
        "espesor_mm": 6,
        "U_W_m2K": 3.5,
        "transmitancia_solar": 0.80,
        "color": "#ebcb8b",
        "icono": "🧱",
    },
    "policarbonato_10mm": {
        "nombre": "Policarbonato Alveolar (10mm)",
        "descripcion": "Placa alveolar gruesa. Máximo aislamiento térmico, ideal para climas fríos.",
        "lambda_W_mK": 0.20,
        "espesor_mm": 10,
        "U_W_m2K": 2.8,
        "transmitancia_solar": 0.72,
        "color": "#d08770",
        "icono": "🏗️",
    },
}


def calcular_k(material_id: str, area_m2: float, volumen_m3: float) -> float:
    """
    Calcula la constante k del modelo térmico a partir de la transmitancia U.
    
    La constante k determina la velocidad de intercambio térmico entre
    el interior y el exterior del invernadero.
    
    Fórmula:
        k = (U × A) / (ρ_aire × V × Cp_aire)
    
    Donde:
        U = Transmitancia térmica global del material [W/(m²·K)]
        A = Área total de la cubierta [m²]
        ρ_aire = Densidad del aire [kg/m³]
        V = Volumen interior del invernadero [m³]
        Cp_aire = Calor específico del aire [J/(kg·K)]
    
    Retorna:
        k en [1/s] — se convierte a [1/min] para la simulación
    
    Raises:
        ValueError: Si el material no existe o los parámetros son inválidos
    """
    if material_id not in MATERIALES:
        raise ValueError(f"Material '{material_id}' no encontrado en el catálogo.")
    if area_m2 <= 0 or volumen_m3 <= 0:
        raise ValueError("Área y volumen deben ser positivos.")
    
    U = MATERIALES[material_id]["U_W_m2K"]
    
    # k en [1/s]
    k_por_segundo = (U * area_m2) / (RHO_AIRE * volumen_m3 * CP_AIRE)
    
    # Convertir a [1/min] para el paso de simulación
    k_por_minuto = k_por_segundo * 60.0
    
    return k_por_minuto


def obtener_transmitancia_solar(material_id: str) -> float:
    """Retorna la fracción de radiación solar que transmite el material."""
    if material_id not in MATERIALES:
        raise ValueError(f"Material '{material_id}' no encontrado.")
    return MATERIALES[material_id]["transmitancia_solar"]


def obtener_materiales_lista() -> list[dict]:
    """Retorna la lista de materiales formateada para el frontend."""
    resultado = []
    for mat_id, mat in MATERIALES.items():
        resultado.append({
            "id": mat_id,
            "nombre": mat["nombre"],
            "descripcion": mat["descripcion"],
            "lambda": mat["lambda_W_mK"],
            "U": mat["U_W_m2K"],
            "espesor_mm": mat["espesor_mm"],
            "transmitancia_solar": mat["transmitancia_solar"],
            "color": mat["color"],
            "icono": mat["icono"],
        })
    return resultado


def calcular_area_cubierta(largo: float, ancho: float, alto: float) -> float:
    """
    Calcula el área total aproximada de la cubierta del invernadero.
    Asume forma rectangular con techo a dos aguas simple.
    
    A_total = 2 × (largo × alto) + 2 × (ancho × alto) + largo × ancho
              paredes laterales    paredes frontales      techo (aprox)
    """
    paredes_laterales = 2 * largo * alto
    paredes_frontales = 2 * ancho * alto
    techo = largo * ancho  # Aproximación: techo plano ≈ área base
    return paredes_laterales + paredes_frontales + techo


def calcular_volumen(largo: float, ancho: float, alto: float) -> float:
    """Calcula el volumen interior del invernadero."""
    return largo * ancho * alto
