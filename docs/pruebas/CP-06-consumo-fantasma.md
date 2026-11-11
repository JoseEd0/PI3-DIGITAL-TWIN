# CP-06 · Auditoría del consumo fantasma — **datos simulados**

> Generado con `cd demo/servidor && .venv/bin/python -m gemelo.auditoria`. No editar a mano.
> **Rótulo: simulado.** Compara la estimación por proxy del sistema (luces del BH1750 + aula vacía
> del MLX90640 × potencias del inventario) con la potencia que conoce el simulador. Valida la
> lógica del método; la exactitud real queda **pendiente** hasta revisar el inventario del aula y
> contrastar con un medidor en S15.

Criterio propio: error de la energía estimada ≤ ±15% frente a la verdad simulada contada desde que vence la tolerancia del RA-08, y cero falsos positivos cuando no hay fantasma.

| Caso | Escenario | Verdad total (kWh) | Verdad tras tolerancia (kWh) | Estimado (kWh) | Error | Episodios | Minutos | Costo estimado | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| A | Todos salen a las 10:30 y dejan luces y la mitad de los PC encendidos (2 h) | 1.128 | 1.034 | 1.078 | +4.3% | 1 | 110 | S/ 0.73 | ✅ |
| B | Día normal de 07:00 a 22:00: al terminar la última clase el simulador decide al azar si alguien olvida las luces | 1.128 | 1.034 | 1.078 | +4.3% | 1 | 110 | S/ 0.73 | ✅ |
| C | Noche de 21:30 a 03:30 con el aula apagada: no debe haber falsos positivos | 0.000 | 0.000 | 0.000 | — | 0 | 0 | S/ 0.00 | ✅ |

## Cómo leerlo

- **Verdad total**: todo lo que el aula vacía consumió de más (luces, PC encendidos por encima de su
  consumo en espera y aire acondicionado), desde el primer minuto.
- **Verdad tras tolerancia**: lo mismo, pero solo desde que se cumple el umbral de alerta del RA-08
  (`config/requisitos_ra.yaml`). Es lo que el sistema intenta estimar: los primeros minutos no
  cuentan como olvido.
- La diferencia entre estimado y verdad viene de la fracción supuesta de PC encendidos
  (`energia.fraccion_de_pcs_olvidados_con_luces`) y de la demora en detectar que el aula quedó vacía.
