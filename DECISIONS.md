# Decisiones de diseño

Registro de decisiones tomadas o diferidas, con su justificación.
Actualizar este archivo cada vez que se tome una decisión significativa.

---

## Diferidas

### Screen como modelo separado
**Estado:** diferido para una fase posterior  
**Decisión:** Actualmente `Showtime.screen` es un `CharField` simple.
En el futuro debe convertirse en un modelo `Screen` con `ForeignKey` a `Cinema`,
y `Showtime.screen` pasará a ser `ForeignKey` a `Screen`.  
**Justificación:** Las salas son entidades del cine con identidad propia.
Un modelo separado permitirá asociarles capacidad, tecnología (IMAX, Dolby, etc.)
y otras características.  
**Impacto esperado al implementar:** migración de datos, ajuste de factories
(`ShowtimeFactory` usará `ScreenFactory`), actualización de `__str__` y
de `unique_showtime_per_screen` constraint.

---

## Tomadas

### Los 2x1 son por medio de pago, no por película
**Fecha:** inicio del proyecto  
**Decisión:** El modelo `Promotion` está asociado a `Cinema`, no a `Movie` ni a `Showtime`.
Todas las funciones de un cine son elegibles para el 2x1 si el usuario
tiene el medio de pago correspondiente.  
**Justificación:** Así funcionan realmente las promociones en Argentina
(Santander en Cinépolis, Ualá en Atlas, etc.).

### Scraping: empezar por Showcase y Atlas
**Fecha:** inicio del proyecto  
**Decisión:** Para la Fase 3 (scraping), comenzar por Showcase y Atlas
por tener HTML más estable. Cinemark/Hoyts y Village usan SPAs pesadas
y se abordan después.  
**Alternativa:** Si el scraping de un cine resulta inviable, usar
carteleras de La Nación o Clarín como fuente alternativa.
