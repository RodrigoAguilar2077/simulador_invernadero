"""
Motor térmico del simulador de invernadero.

"""

import numpy as np
from scipy import signal


class ThermalEngine:
    """
    Motor de simulación térmica para invernaderos
    """

    def __init__(self, k: float, alpha: float = 0.005):
        """
        Args:
            k: Constante de transferencia térmica [1/min].
               Valores típicos: 0.007 (policarbonato 10mm) a 0.018 (polietileno LDPE).
            alpha: Factor de absorción de radiación solar [°C/(W/m²·min)].
                   Representa cuánto contribuye cada W/m² de radiación al calentamiento interior.
        """
        self.k = k
        self.alpha = alpha

    def _f(self, T_int: float, T_ext: float, radiacion: float) -> float:
        """
        Evalúa la derivada dT/dt de la EDO térmica.
        
        dT/dt = k × (T_ext - T_int) + α × Radiación
        
        Args:
            T_int: Temperatura interior actual [°C]
            T_ext: Temperatura exterior actual [°C]
            radiacion: Radiación solar incidente [W/m²]
        
        Returns:
            Tasa de cambio de temperatura [°C/min]
        """
        return self.k * (T_ext - T_int) + self.alpha * radiacion

    def euler_mejorado(
        self,
        T0: float,
        T_ext_array: np.ndarray,
        rad_array: np.ndarray,
        h: float = 1.0,
    ) -> np.ndarray:
        """
        Resuelve la EDO térmica usando el Método de Euler Mejorado (Heun).
        
        El método de Heun es un método de Runge-Kutta de orden 2 que mejora
        la precisión del Euler simple mediante un paso predictor-corrector:
        
            Predictor:  T̃_{n+1} = T_n + h × f(t_n, T_n)
            Corrector:  T_{n+1} = T_n + (h/2) × [f(t_n, T_n) + f(t_{n+1}, T̃_{n+1})]
        
        Args:
            T0: Temperatura interior inicial [°C]
            T_ext_array: Array de temperaturas exteriores, un valor por cada paso de tiempo [°C]
            rad_array: Array de radiación solar, un valor por cada paso de tiempo [W/m²]
            h: Paso de tiempo [min]. Default = 1 minuto.
        
        Returns:
            Array de temperaturas interiores, mismo tamaño que T_ext_array [°C]
        """
        n_steps = len(T_ext_array)
        T_int = np.zeros(n_steps)
        T_int[0] = T0

        for i in range(n_steps - 1):
            T_ext_actual = T_ext_array[i]
            T_ext_siguiente = T_ext_array[i + 1]
            rad_actual = rad_array[i]
            rad_siguiente = rad_array[i + 1]

            # Paso 1 — Predictor (Euler simple)
            f1 = self._f(T_int[i], T_ext_actual, rad_actual)
            T_predicho = T_int[i] + h * f1

            # Paso 2 — Corrector (promedio de pendientes)
            f2 = self._f(T_predicho, T_ext_siguiente, rad_siguiente)
            T_int[i + 1] = T_int[i] + (h / 2.0) * (f1 + f2)

        return T_int

    def laplace_analysis(self) -> dict:
        """
        Realiza el análisis de Laplace de la función de transferencia del invernadero.
        
        La EDO linealizada (sin radiación) es:
            dT_int/dt + k × T_int = k × T_ext
        
        Aplicando Transformada de Laplace:
            s × T_int(s) + k × T_int(s) = k × T_ext(s)
            
            H(s) = T_int(s) / T_ext(s) = k / (s + k)
        
        Esta es una función de transferencia de primer orden con:
            - Polo en s = -k
            - Constante de tiempo τ = 1/k [minutos]
            - Ganancia estática = 1 (en estado estable, T_int → T_ext)
        
        Returns:
            Diccionario con el análisis completo:
                - tau_minutos: Constante de tiempo [min]
                - tau_horas: Constante de tiempo [h]
                - polo: Ubicación del polo en el plano s
                - ganancia_estatica: Ganancia DC del sistema
                - tiempo_estabilizacion_min: Tiempo para alcanzar ~98% (4τ)
                - clasificacion: "rápido", "medio", o "lento"
                - step_response_t: Vector de tiempo de la respuesta al escalón
                - step_response_y: Vector de amplitud de la respuesta al escalón
        """
        # Constante de tiempo
        tau = 1.0 / self.k  # en minutos
        tau_horas = tau / 60.0

        # Polo del sistema
        polo = -self.k

        # Tiempo de estabilización (4τ para ~98.2% del valor final)
        t_estabilizacion = 4 * tau

        # Clasificación basada en la constante de tiempo
        if tau < 40:
            clasificacion = "rápido"
            descripcion = "El invernadero responde rápidamente a cambios exteriores. Poca inercia térmica."
        elif tau < 90:
            clasificacion = "medio"
            descripcion = "Respuesta moderada. Balance entre reactividad y retención de calor."
        else:
            clasificacion = "lento"
            descripcion = "Alta inercia térmica. Excelente retención de calor, respuesta lenta a cambios."

        # Respuesta al escalón usando scipy.signal
        # H(s) = k / (s + k) → numerador = [k], denominador = [1, k]
        sistema = signal.TransferFunction([self.k], [1, self.k])
        
        # Generar respuesta al escalón unitario (0 a 6τ)
        t_max = min(6 * tau, 1440)  # Máximo 24 horas
        t = np.linspace(0, t_max, 500)
        t_out, y_out = signal.step(sistema, T=t)

        return {
            "tau_minutos": round(tau, 2),
            "tau_horas": round(tau_horas, 2),
            "polo": round(polo, 6),
            "ganancia_estatica": 1.0,
            "tiempo_estabilizacion_min": round(t_estabilizacion, 2),
            "tiempo_estabilizacion_horas": round(t_estabilizacion / 60, 2),
            "clasificacion": clasificacion,
            "descripcion": descripcion,
            "step_response_t": t_out.tolist(),
            "step_response_y": y_out.tolist(),
        }

    def simular(
        self,
        T0: float,
        T_ext_array: np.ndarray,
        rad_array: np.ndarray,
        h: float = 1.0,
    ) -> dict:
        """
        Ejecuta una simulación completa y retorna resultados formateados.
        
        Args:
            T0: Temperatura interior inicial [°C]
            T_ext_array: Temperaturas exteriores [°C]
            rad_array: Radiación solar [W/m²]
            h: Paso de tiempo [min]
        
        Returns:
            Diccionario con:
                - tiempo_min: Lista de minutos [0, 1, 2, ..., n]
                - tiempo_horas: Lista de horas decimales [0.0, 0.0167, ...]
                - T_interior: Lista de temperaturas interiores [°C]
                - T_exterior: Lista de temperaturas exteriores [°C]
                - radiacion: Lista de radiación solar [W/m²]
                - T_max_int: Temperatura máxima interior [°C]
                - T_min_int: Temperatura mínima interior [°C]
                - T_promedio_int: Temperatura promedio interior [°C]
        """
        T_int = self.euler_mejorado(T0, T_ext_array, rad_array, h)
        n = len(T_int)
        tiempo_min = np.arange(n) * h
        tiempo_horas = tiempo_min / 60.0

        return {
            "tiempo_min": tiempo_min.tolist(),
            "tiempo_horas": tiempo_horas.tolist(),
            "T_interior": np.round(T_int, 2).tolist(),
            "T_exterior": np.round(T_ext_array, 2).tolist(),
            "radiacion": np.round(rad_array, 2).tolist(),
            "T_max_int": round(float(np.max(T_int)), 2),
            "T_min_int": round(float(np.min(T_int)), 2),
            "T_promedio_int": round(float(np.mean(T_int)), 2),
        }
