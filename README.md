# AgroTech: Simulador de Inercia Térmica para Invernaderos

![Versión](https://img.shields.io/badge/Version-1.0.0-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Vue](https://img.shields.io/badge/Frontend-Vue.js-4fc08d)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)

Este proyecto es una herramienta de ingeniería diseñada para modelar y predecir el comportamiento climático dentro de un invernadero. Utiliza métodos numéricos avanzados y teoría de control para ayudar a agricultores y técnicos a entender cómo el material y las dimensiones de una estructura afectan la protección de sus cultivos.

---

## Características Principales

- **Simulación en Tiempo Real:** Cálculo minuto a minuto de la temperatura interna basado en leyes físicas.
- **Clima Dinámico y Geolocalización:** Integración con la API de OpenWeatherMap y la API de Geolocalización del navegador para simular condiciones reales automáticamente según tu ubicación.
- **Análisis de Materiales:** Comparativa de eficiencia térmica entre diferentes cubiertas.
- **Interfaz Glassmorphism:** Diseño minimalista, limpio y responsivo.
- **Modo Ingeniero:** Visualización de la matemática detrás del simulador.

---

## Fundamentos Matemáticos

El simulador se basa en un motor de cálculo robusto:

### 1. Método de Euler Mejorado (Heun)
Para resolver la Ecuación Diferencial Ordinaria (EDO) de transferencia de calor, implementamos el algoritmo de **Heun**. Utiliza un predictor y un corrector para reducir el error de truncamiento, asegurando que la curva de temperatura sea estable.

### 2. Análisis de Laplace
Aplicamos la **Transformada de Laplace** para obtener la Función de Transferencia H(s) del sistema:
H(s) = k / (s + k)

Esto permite calcular la **Constante de Tiempo (tau)**, que define la inercia térmica del invernadero. Un sistema con una constante alta es más estable frente a cambios de temperatura.

---

## Stack Tecnológico

* **Frontend:** Vue.js 3 + CSS Nativo (Estética Glassmorphism).
* **Backend:** FastAPI (Python) para el procesamiento rápido de cálculos.
* **Matemáticas:** NumPy y SciPy para análisis térmicos.
* **Datos:** API de OpenWeatherMap.

---

## Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/RodrigoAguilar2077/simulador_invernadero
   cd simulador_invernadero
   ```

2. **Configurar Backend:**
   ```bash
   cd backend
   python -m venv venv
   # En Windows: venv\Scripts\activate
   # En Linux/Mac: source venv/bin/activate
   pip install -r requirements.txt
   ```
   

   Ejecuta el servidor:
   ```bash
   uvicorn main:app --reload
   ```

3. **Configurar Frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

4. **Acceder a la Aplicación:**
   Abre tu navegador en `http://localhost:5173` y acepta los permisos de ubicación para cargar tu clima local.