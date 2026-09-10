// Plano 2D del L-419. Es la parte que hace de gemelo: el aula se ve como es y
// cada nodo está donde se va a instalar (docs/02-instrumentacion-l419.md).

const MURO = { x: 60, y: 50, ancho: 1080, alto: 450 }

// Las luminarias van en el techo, entre las filas de mesas: por eso su fila
// intermedia no coincide con ninguna mesa.
// Las luminarias van sobre los pasillos, entre filas de mesas, como en el techo
// real: así ninguna cae encima de una mesa ni de una etiqueta.
const LUMINARIAS = [
  [300, 240], [600, 240], [900, 240],
  [300, 336], [600, 336], [900, 336],
]

const MESAS = []
for (let fila = 0; fila < 3; fila += 1) {
  for (let columna = 0; columna < 4; columna += 1) {
    MESAS.push([175 + columna * 205, 168 + fila * 96])
  }
}

const NODOS = [
  { id: 'energia', x: 92, y: 105, etiqueta: 'Energía', ancla: 'start' },
  { id: 'audio', x: 600, y: 90, etiqueta: 'Audio', ancla: 'middle' },
  { id: 'ambiental', x: 600, y: 398, etiqueta: 'Ambiental', ancla: 'middle' },
  { id: 'ocupacion-fondo', x: 1020, y: 398, etiqueta: 'Ocupación (fondo)', ancla: 'end' },
  { id: 'ocupacion-puerta', x: 230, y: 452, etiqueta: 'Ocupación (puerta)', ancla: 'start' },
  { id: 'puerta', x: 128, y: 478, etiqueta: 'Puerta', ancla: 'start' },
]

function colorDelNodo(nodo, salud, alertas) {
  const fila = salud.find((s) => s.nodo === nodo)
  if (fila?.caido) return 'var(--apagado)'
  const alerta = alertas.find((a) => a.nodo === nodo)
  if (alerta?.severidad === 'critica') return 'var(--critico)'
  if (alerta) return 'var(--atencion)'
  return 'var(--petroleo)'
}

export default function PlanoDelAula({ resumen, salud, alertas }) {
  const personas = Math.min(resumen.conteo ?? 0, 24)
  const luces = resumen.lucesEncendidas
  const puertaAbierta = resumen.puertaAbierta
  const base = MURO.y + MURO.alto

  return (
    <>
      <svg
        className="plano"
        viewBox="0 0 1200 540"
        role="img"
        aria-label={`Plano del laboratorio: ${personas} personas estimadas, luces ${luces ? 'encendidas' : 'apagadas'}, puerta ${puertaAbierta ? 'abierta' : 'cerrada'}`}
      >
        <rect {...{ x: MURO.x, y: MURO.y, width: MURO.ancho, height: MURO.alto }}
          fill="var(--panel-hundido)" stroke="var(--linea-fuerte)" strokeWidth="4" />

        {/* ventanas del muro norte */}
        {[290, 560, 830].map((x) => (
          <rect key={x} x={x} y={MURO.y - 8} width="160" height="16" fill="var(--panel)"
            stroke="var(--linea-fuerte)" strokeWidth="3" />
        ))}

        {/* tablero eléctrico junto al muro oeste */}
        <rect x={MURO.x + 4} y="82" width="24" height="76" fill="var(--panel)"
          stroke="var(--linea-fuerte)" strokeWidth="3" />

        {/* luminarias del techo */}
        {LUMINARIAS.map(([x, y]) => (
          <rect key={`${x}-${y}`} x={x - 50} y={y - 6} width="100" height="12" rx="3"
            fill={luces ? 'var(--carga-iluminacion)' : 'var(--panel)'}
            stroke="var(--linea)" strokeWidth="2" opacity={luces ? 0.85 : 1} />
        ))}

        {/* mesas de trabajo, con una persona por puesto ocupado */}
        {MESAS.map(([x, y], indice) => (
          <g key={`${x}-${y}`}>
            <rect x={x} y={y} width="140" height="48" rx="3" fill="var(--panel)"
              stroke="var(--linea)" strokeWidth="2" />
            {indice * 2 < personas && <circle cx={x + 40} cy={y + 24} r="13" fill="var(--tinta-media)" />}
            {indice * 2 + 1 < personas && <circle cx={x + 100} cy={y + 24} r="13" fill="var(--tinta-media)" />}
          </g>
        ))}

        {/* pizarra y proyector al fondo */}
        <rect x={MURO.x + MURO.ancho - 36} y="190" width="26" height="150" rx="3"
          fill="var(--panel)" stroke="var(--linea)" strokeWidth="2" />
        <text x={MURO.x + MURO.ancho - 46} y="270" textAnchor="end" fontSize="17" fill="var(--tinta-tenue)">
          Pizarra
        </text>

        {/* puerta en el muro sur */}
        <rect x="140" y={base - 8} width="150" height="16"
          fill={puertaAbierta ? 'var(--critico)' : 'var(--panel)'}
          stroke="var(--linea-fuerte)" strokeWidth="3" />
        {puertaAbierta && (
          <path d={`M290 ${base} A150 150 0 0 0 290 ${base - 150}`} fill="none"
            stroke="var(--critico)" strokeWidth="3" strokeDasharray="6 6" />
        )}
        <text x="215" y={base + 32} textAnchor="middle" fontSize="19" fill="var(--tinta-media)">
          {puertaAbierta ? 'Puerta abierta' : 'Puerta cerrada'}
        </text>

        {/* nodos instalados */}
        {NODOS.map((nodo) => {
          const color = colorDelNodo(nodo.id, salud, alertas)
          const desplazamiento = nodo.ancla === 'end' ? -20 : nodo.ancla === 'start' ? 20 : 0
          return (
            <g key={nodo.id}>
              <circle cx={nodo.x} cy={nodo.y} r="12" fill={color} stroke="var(--panel)" strokeWidth="3" />
              <text
                x={nodo.x + desplazamiento}
                y={nodo.ancla === 'middle' ? nodo.y - 22 : nodo.y + 6}
                textAnchor={nodo.ancla}
                fontSize="19"
                fill="var(--tinta)"
              >
                {nodo.etiqueta}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="plano-leyenda">
        <span><i className="muestra-de-color" style={{ background: 'var(--petroleo)' }} />Nodo reportando</span>
        <span><i className="muestra-de-color" style={{ background: 'var(--atencion)' }} />Con alerta</span>
        <span><i className="muestra-de-color" style={{ background: 'var(--apagado)' }} />Sin reportar</span>
        <span><i className="muestra-de-color" style={{ background: 'var(--carga-iluminacion)' }} />Luminaria encendida</span>
      </div>
    </>
  )
}
