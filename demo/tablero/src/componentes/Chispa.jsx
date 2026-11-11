import React from 'react'

const ANCHO = 160
const ALTO = 34

// Tendencia mínima de una magnitud (últimos puntos recibidos).
export default function Chispa({ puntos }) {
  const valores = puntos.map(([, v]) => Number(v)).filter((v) => !Number.isNaN(v))
  if (valores.length < 2) return <svg className="chispa" width={ANCHO} height={ALTO} aria-hidden="true" />
  const minimo = Math.min(...valores)
  const rango = Math.max(...valores) - minimo || 1
  const trazo = valores
    .map((v, i) => `${((i / (valores.length - 1)) * ANCHO).toFixed(1)},${(ALTO - 3 - ((v - minimo) / rango) * (ALTO - 6)).toFixed(1)}`)
    .join(' ')
  return (
    <svg className="chispa" width={ANCHO} height={ALTO} viewBox={`0 0 ${ANCHO} ${ALTO}`} aria-hidden="true">
      <polyline points={trazo} fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  )
}
