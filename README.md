# 🌱 AgroTech: Simulador de Inercia Térmica para Invernaderos

![Versión](https://img.shields.io/badge/Version-1.0.0-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Vue](https://img.shields.io/badge/Frontend-Vue.js-4fc08d)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)

Este proyecto es una herramienta de ingeniería diseñada para modelar y predecir el comportamiento climático dentro de un invernadero. Utiliza métodos numéricos avanzados y teoría de control para ayudar a agricultores y técnicos a entender cómo el material y las dimensiones de una estructura afectan la protección de sus cultivos.

---

## 🚀 Características Principales

- **Simulación en Tiempo Real:** Cálculo minuto a minuto de la temperatura interna basado en leyes físicas.
- **Clima Dinámico:** Integración con la API de OpenWeatherMap para simular condiciones reales de cualquier ciudad del mundo.
- **Análisis de Materiales:** Comparativa de eficiencia térmica entre Vidrio, Policarbonato y Polietileno.
- **Interfaz Glassmorphism:** Diseño minimalista y moderno con enfoque en la experiencia de usuario (UX).
- **Modo Ingeniero:** Visualización de las tripas matemáticas del simulador.

---

## 🧠 Fundamentos Matemáticos

El simulador no es solo visual; corre sobre un motor de cálculo robusto:

### 1. Método de Euler Mejorado (Heun)
Para resolver la Ecuación Diferencial Ordinaria (EDO) de transferencia de calor, implementamos el algoritmo de **Heun**. A diferencia del Euler simple, este utiliza un predictor y un corrector para reducir el error de truncamiento, asegurando que la curva de temperatura sea estable y precisa.

### 2. Análisis de Laplace
Aplicamos la **Transformada de Laplace** para obtener la Función de Transferencia $H(s)$ del sistema:
$$H(s) = \frac{k}{s + k}$$
Esto nos permite calcular la **Constante de Tiempo ($\tau$)**, que define la inercia térmica del invernadero. Un sistema con una $\tau$ alta es más estable frente a heladas repentinas.

---

## 🛠️ Stack Tecnológico

* **Frontend:** Vue.js 3 + Vite + Tailwind CSS (Estética Glassmorphism).
* **Backend:** FastAPI (Python) para el procesamiento de alta velocidad de los algoritmos.
* **Matemáticas:** NumPy para álgebra lineal y manejo de vectores térmicos.
* **Datos:** API de OpenWeatherMap para geolocalización y clima.

---

## 📦 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/RodrigoAguilar2077/simulador_invernadero.git](https://github.com/RodrigoAguilar2077/simulador_invernadero.git)
   cd simulador_invernadero