# Grafos causales por requisito de alto nivel

Un archivo por RA (`ra-XX-*.yaml`). Los lee `demo/servidor/gemelo/grafos.py` y los evalúa el motor
SymCure de `gemelo/razonamiento.py`. Las figuras se generan con
`demo/servidor/.venv/bin/python -m gemelo.figuras` y quedan en `grafos/figuras/`.

## Formato

```yaml
ra: RA-03                       # requisito de alto nivel (config/requisitos_ra.yaml)
titulo: CO2 alto en el aula
evento_central: co2_alto        # la violación del RA
eventos:
  - id: puerta_cerrada_prolongada
    texto: Puerta cerrada más de 30 min con gente
    clase: causa                # causa (raíz) | condicion (contexto observado) | intermedio | sintoma | efecto
    entrada: OR                 # OR | AND | NM (con `fraccion`) | IF (con `condicion`)
    salida: OR                  # AND: produce siempre todos sus efectos; OR: solo algunos
    observable:                 # si falta, el evento es INFERIDO
      sensor: "KY-024 (nodo 6)"
      todas:
        - {campo: derivado.puerta_abierta, op: "==", valor: false}
        - {campo: derivado.minutos_puerta_cerrada, op: ">=", valor: 30}
    recomendacion: Abrir la puerta o las ventanas 5 minutos
aristas:
  - [puerta_cerrada_prolongada, ventilacion_insuficiente]   # causa → efecto
```

Un `observable` puede ser:

- `{campo, op, valor}`, con `op` igual a `==`, `!=`, `>`, `>=`, `<`, `<=`, `contiene` o `no_contiene`;
- `{ra: RA-0X}`, que es verdadero cuando ese RA está en alerta o crítico;
- `{todas: [...]}` o `{alguna: [...]}`.

Los campos se nombran `<tipo>.<campo del Gateway>` o `derivado.<nombre>`. Ver
`docs/CONTRATO_DATOS.md` y `gemelo/estado.py`.
