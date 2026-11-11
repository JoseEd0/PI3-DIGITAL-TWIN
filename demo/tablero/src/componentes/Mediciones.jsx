import React from 'react'
import Chispa from './Chispa.jsx'
import { TIPOS, decimalesDe, hora, numero } from '../formato.js'

const DETALLES = {
  co2: [['delta_30s', 'Δ 30 s', 'ppm'], ['nivel', 'Nivel', '']],
  audio: [['lmax_db', 'Máx', 'dB'], ['base_db', 'Fondo', 'dB']],
  gas: [['v_ao', 'Salida', 'V'], ['calentando', 'Calentando', '']],
  luz: [['lux', 'Techo', 'lx'], ['luces_cambio', 'Cambio de luces', '']],
  termico: [['entradas', 'Entradas', ''], ['salidas', 'Salidas', '']],
  magnetico: [['aperturas', 'Aperturas', ''], ['campo_raw', 'ADC', '']],
  ambiente: [['hum_pct', 'Humedad', '%'], ['pres_hpa', 'Presión', 'hPa']],
}

function valorPrincipal(m) {
  if (m.tipo === 'magnetico') return m.valor === null ? '—' : m.valor ? 'Abierta' : 'Cerrada'
  return numero(m.valor, decimalesDe(m.tipo))
}

// Mínimo 1 de la pauta EC3: las mediciones, con unidad, tendencia y detalle del nodo.
export default function Mediciones({ mediciones, salud, elegido, alElegir }) {
  const porNodo = Object.fromEntries(salud.map((s) => [s.nodo, s]))
  return (
    <section className="panel mediciones">
      <h2>Mediciones de los 7 nodos</h2>
      <div className="tarjetas">
        {mediciones.map((m) => {
          const s = porNodo[m.nodo]
          return (
            <button key={m.nodo} className={`tarjeta ${s?.caido ? 'caido' : ''} ${elegido === m.nodo ? 'elegido' : ''}`}
                    onClick={() => alElegir(elegido === m.nodo ? null : m.nodo)}>
              <span className="tarjeta-cabecera">
                <span>{TIPOS[m.tipo].icono} {TIPOS[m.tipo].nombre}</span>
                <span className="nodo">nodo {m.nodo}</span>
              </span>
              <span className="tarjeta-valor">
                {valorPrincipal(m)} <small>{m.tipo === 'magnetico' ? '' : m.unidad}</small>
              </span>
              <Chispa puntos={m.tendencia} />
              <span className="tarjeta-sensor">{m.sensor}</span>
              {m.anomalias.length > 0 && <span className="anomalias">{m.anomalias.join(' · ')}</span>}
              {elegido === m.nodo && (
                <span className="detalle">
                  {DETALLES[m.tipo].map(([campo, etiqueta, unidad]) => (
                    <span key={campo}>{etiqueta}: {numero(m.campos[campo], 1)} {unidad}</span>
                  ))}
                  <span>Último dato: {hora(m.ts)} · seq {s?.seq ?? '—'} · perdidos {s?.perdidos ?? '—'}</span>
                  <span>Programa: {s?.programa}</span>
                </span>
              )}
            </button>
          )
        })}
      </div>
    </section>
  )
}
