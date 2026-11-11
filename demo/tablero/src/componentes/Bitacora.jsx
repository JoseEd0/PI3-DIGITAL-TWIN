import React, { useEffect, useState } from 'react'
import { leer } from '../useGemelo.js'
import { hora } from '../formato.js'

const TIPOS_DE_EVENTO = ['', 'requisito', 'puerta', 'ocupacion', 'luces', 'anomalia_nodo', 'salud', 'gateway', 'escenario']
const SEVERIDADES = ['', 'info', 'alerta', 'critico']

// Footprint del aula: el log de eventos que pide el proyecto, con filtros y exportación a CSV.
export default function Bitacora({ eventosRecientes }) {
  const [tipo, setTipo] = useState('')
  const [severidad, setSeveridad] = useState('')
  const [eventos, setEventos] = useState(eventosRecientes)
  const consulta = new URLSearchParams({ ...(tipo && { tipo }), ...(severidad && { severidad }), limite: 100 })

  useEffect(() => {
    leer(`/api/eventos?${consulta}`).then(setEventos).catch(() => {})
  }, [tipo, severidad, eventosRecientes[0]?.ts, eventosRecientes.length])

  return (
    <section className="panel bitacora">
      <header className="bitacora-cabecera">
        <h2>Log de eventos (footprint)</h2>
        <label>Tipo <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          {TIPOS_DE_EVENTO.map((t) => <option key={t} value={t}>{t || 'todos'}</option>)}
        </select></label>
        <label>Severidad <select value={severidad} onChange={(e) => setSeveridad(e.target.value)}>
          {SEVERIDADES.map((s) => <option key={s} value={s}>{s || 'todas'}</option>)}
        </select></label>
        <a className="boton" href={`/api/eventos.csv?${consulta}`}>Exportar CSV</a>
      </header>
      <table>
        <thead><tr><th>Hora</th><th>Severidad</th><th>Tipo</th><th>Evento</th><th>Causas / recomendación</th><th>Origen</th></tr></thead>
        <tbody>
          {eventos.map((e, i) => (
            <tr key={`${e.ts}-${i}`} className={e.severidad}>
              <td>{hora(e.ts)}</td><td>{e.severidad}</td><td>{e.tipo}</td><td>{e.mensaje}</td>
              <td>{[...e.causas.slice(0, 2), ...e.recomendaciones.slice(0, 1).map((r) => `→ ${r}`)].join(' · ')}</td>
              <td>{e.origen}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
