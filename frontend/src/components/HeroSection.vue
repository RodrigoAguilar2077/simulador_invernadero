<template>
  <section class="hero" id="section-intro">
    <div class="hero__header">
      <h1 class="hero__title">Optimización Microclimática</h1>
      <p class="hero__subtitle">
        Descubre cómo el material y la geometría de tu invernadero protegen el cultivo,
        optimizan el consumo de agua y aumentan el rendimiento por metro cuadrado.
      </p>
    </div>

    <div class="hero__cards">
      <div class="hero__card glass-card fade-in-up" style="animation-delay: 0.1s">
        <div class="hero__card-icon">
          <Droplets size="32" stroke-width="1.5" />
        </div>
        <h3 class="hero__card-title">Ahorro de Agua</h3>
        <p class="hero__card-text">Hasta 50% menos consumo hídrico gracias al microclima controlado y la reducción de evapotranspiración.</p>
      </div>

      <div class="hero__card glass-card fade-in-up" style="animation-delay: 0.25s">
        <div class="hero__card-icon hero__card-icon--amber">
          <ThermometerSnowflake size="32" stroke-width="1.5" />
        </div>
        <h3 class="hero__card-title">Protección contra Heladas</h3>
        <p class="hero__card-text">Aísla los cultivos de temperaturas extremas. La cubierta actúa como barrera térmica contra el frío nocturno.</p>
      </div>

      <div class="hero__card glass-card fade-in-up" style="animation-delay: 0.4s">
        <div class="hero__card-icon hero__card-icon--blue">
          <TrendingUp size="32" stroke-width="1.5" />
        </div>
        <h3 class="hero__card-title">Aumento de Rendimiento</h3>
        <p class="hero__card-text">2-3× más producción por m² al extender ciclos de cultivo y controlar variables ambientales.</p>
      </div>
    </div>

    <div class="hero__math-block glass-card fade-in-up" style="animation-delay: 0.55s">
      <h3 class="hero__math-title">El Rol de la Matemática</h3>
      <div class="hero__math-grid">
        <div class="hero__math-item">
          <div class="hero__math-badge hero__math-badge--purple">Euler Mejorado</div>
          <p class="hero__math-desc"><strong>El Reloj de Precisión.</strong> Resuelve la ecuación diferencial de calor minuto a minuto para predecir la temperatura interior.</p>
          <code class="hero__math-eq">T(t+1) = T(t) + (h/2)[f(t) + f(t+1, T̃)]</code>
        </div>
        <div class="hero__math-divider"></div>
        <div class="hero__math-item">
          <div class="hero__math-badge hero__math-badge--amber">Laplace</div>
          <p class="hero__math-desc"><strong>El Estetoscopio.</strong> Analiza la función de transferencia H(s) para medir la inercia térmica (Time Constant τ) y estabilidad del sistema.</p>
          <code class="hero__math-eq">H(s) = k / (s + k) → τ = 1/k</code>
        </div>
      </div>
    </div>

    <button class="btn btn--primary hero__cta" @click="$emit('scroll-to-simulator')">
      Comenzar Simulación
    </button>
  </section>
</template>

<script setup>
import { Droplets, ThermometerSnowflake, TrendingUp } from 'lucide-vue-next'

defineEmits(['scroll-to-simulator'])
</script>

<style scoped>
.hero { text-align: center; max-width: 960px; margin: 0 auto; }
.hero__title {
  font-size: var(--font-size-3xl); font-weight: 800;
  background: linear-gradient(135deg, var(--color-purple-300), var(--color-purple-500), var(--color-amber-400));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; margin-bottom: var(--space-md);
}
.hero__subtitle {
  font-size: var(--font-size-base); color: var(--color-text-secondary);
  max-width: 640px; margin: 0 auto var(--space-xl); line-height: 1.7;
}
.hero__cards { display: flex; flex-direction: row; gap: var(--space-lg); margin-bottom: var(--space-xl); }
.hero__card { flex: 1; padding: var(--space-xl) var(--space-lg); text-align: center; }
.hero__card-icon {
  width: 56px; height: 56px; border-radius: var(--radius-md);
  background: rgba(192,132,252,0.1); color: var(--color-purple-400);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto var(--space-md);
}
.hero__card-icon--amber { background: rgba(251,191,36,0.1); color: var(--color-amber-400); }
.hero__card-icon--blue { background: rgba(96,165,250,0.1); color: var(--color-blue-400); }
.hero__card-title { font-size: var(--font-size-base); font-weight: 700; margin-bottom: var(--space-sm); }
.hero__card-text { font-size: var(--font-size-sm); color: var(--color-text-muted); line-height: 1.6; }

.hero__math-block { padding: var(--space-xl); margin-bottom: var(--space-xl); text-align: left; }
.hero__math-title {
  font-size: var(--font-size-lg); font-weight: 700; text-align: center;
  margin-bottom: var(--space-lg); color: var(--color-text-primary);
}
.hero__math-grid { display: grid; grid-template-columns: 1fr auto 1fr; gap: var(--space-lg); align-items: start; }
.hero__math-divider { width: 1px; background: var(--glass-border); align-self: stretch; }
.hero__math-badge {
  display: inline-block; padding: 2px 12px; border-radius: var(--radius-full);
  font-size: var(--font-size-xs); font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin-bottom: var(--space-sm);
}
.hero__math-badge--purple { background: rgba(192,132,252,0.12); color: var(--color-purple-400); }
.hero__math-badge--amber { background: rgba(251,191,36,0.12); color: var(--color-amber-400); }
.hero__math-desc { font-size: var(--font-size-sm); color: var(--color-text-secondary); line-height: 1.6; margin-bottom: var(--space-sm); }
.hero__math-eq {
  display: block; padding: var(--space-sm) var(--space-md);
  background: rgba(0,0,0,0.3); border-radius: var(--radius-sm);
  font-family: 'Courier New', monospace; font-size: var(--font-size-sm);
  color: var(--color-purple-300);
}
.hero__cta { padding: var(--space-md) var(--space-2xl); font-size: var(--font-size-base); }

@media (max-width: 768px) {
  .hero__cards { flex-direction: column; }
  .hero__math-grid { grid-template-columns: 1fr; }
  .hero__math-divider { display: none; }
  .hero__title { font-size: var(--font-size-2xl); }
}
</style>
