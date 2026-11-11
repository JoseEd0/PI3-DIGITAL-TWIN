import React, { useEffect, useState } from 'react'
import { leer } from '../useGemelo.js'
import { TIPOS } from '../formato.js'

const ESCALA = 40 // px por metro
const MARGEN = 20

function colorDelNodo(salud, medicion) {
  if (!salud || salud.caido) return 'var(--apagado)'
  if (medicion?.anomalias.some((a) => a.includes('CRITICO') || a === 'GAS_DETECTADO')) return 'var(--critico)'
  if (medicion?.anomalias.length) return 'var(--atencion)'
  return 'var(--bien)'
}

// Plano 2D del aula con los 7 nodos donde los monta el código del docente (posición supuesta).
export default function Plano({ estado, elegido, alElegir }) {
  const [aula, setAula] = useState(null)
  useEffect(() => { leer('/api/aula').then(setAula).catch(() => {}) }, [])
  if (!aula) return <section className="panel plano">Cargando plano…</section>

  const ancho = aula.largo * ESCALA + 2 * MARGEN
  const alto = aula.ancho * ESCALA + 2 * MARGEN
  const salud = Object.fromEntries(estado.salud.map((s) => [s.nodo, s]))
  const mediciones = Object.fromEntries(estado.mediciones.map((m) => [m.nodo, m]))
  const x = (metros) => MARGEN + metros * ESCALA
  const y = (metros) => MARGEN + metros * ESCALA
  const ocupacion = estado.derivados.ocupacion

  return (
    <section className="panel plano">
      <h2>Plano del {aula.nombre}{aula.plano.supuesto && <span className="pastilla atencion">ubicaciones supuestas</span>}</h2>
      <svg viewBox={`0 0 ${ancho} ${alto}`} className="lienzo-plano" role="img" aria-label="Plano del aula con los nodos">
        <rect x={MARGEN} y={MARGEN} width={aula.largo * ESCALA} height={aula.ancho * ESCALA} className="muro" />
        {aula.plano.objetos.map((o, i) => (
          <g key={i} className={`objeto ${o.tipo}`}>
            <rect x={x(o.x) - ((o.ancho ?? 0.6) * ESCALA) / 2} y={y(o.y) - 6} width={(o.ancho ?? 0.6) * ESCALA} height={12} />
            <text x={x(o.x)} y={y(o.y) + 20}>{o.tipo.replace('_', ' ')}</text>
          </g>
        ))}
        {estado.derivados.luces_encendidas && <rect x={MARGEN} y={MARGEN} width={aula.largo * ESCALA} height={aula.ancho * ESCALA} className="luz-encendida" />}
        {Object.entries(aula.plano.nodos).map(([id, n]) => {
          const nodo = Number(id)
          return (
            <g key={id} className={`nodo-plano ${elegido === nodo ? 'elegido' : ''}`} onClick={() => alElegir(elegido === nodo ? null : nodo)}>
              <circle cx={x(n.x)} cy={y(n.y)} r={11} fill={colorDelNodo(salud[nodo], mediciones[nodo])} />
              <text x={x(n.x)} y={y(n.y) + 4} className="numero">{id}</text>
              <title>{`Nodo ${id} · ${TIPOS[mediciones[nodo]?.tipo]?.nombre ?? n.nombre} · ${n.montaje}`}</title>
            </g>
          )
        })}
        <text x={ancho - MARGEN} y={alto - 4} className="leyenda-plano">
          {ocupacion === null ? 'ocupación —' : `${ocupacion} persona(s) dentro`} · puerta {estado.derivados.puerta_abierta ? 'abierta' : 'cerrada'}
        </text>
      </svg>
    </section>
  )
}
