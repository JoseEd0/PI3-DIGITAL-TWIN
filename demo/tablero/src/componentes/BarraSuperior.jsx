import React, { useState } from 'react'
import { enviar } from '../useGemelo.js'

const VELOCIDADES = [1, 10, 60, 240]

export default function BarraSuperior({ estado, conectado }) {
  const { reloj, fuente, aula } = estado
  const [error, setError] = useState(null)
  const supuestos = aula.supuestos
  const grafana = `${window.location.protocol}//${window.location.hostname}:3000`

  const ejecutar = async (ruta) => {
    try {
      setError(null)
      await enviar(ruta)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <header className="barra">
      {fuente.simulado && (
        <div className="franja-simulada" role="status">
          {fuente.reproduccion
            ? <>DATOS REPRODUCIDOS · {fuente.reproduccion.archivo} ({fuente.origen}) ·{' '}
                {fuente.reproduccion.terminado ? 'terminó' : `${Math.round(fuente.reproduccion.avance * 100)} %`}</>
            : <>DATOS SIMULADOS · grupo «{fuente.grupo}» · mismo formato que el Gateway del curso</>}
        </div>
      )}
      <div className="barra-fila">
        <div className="titulo">
          <h1>Campus Twin · {aula.nombre}</h1>
          <span className="subtitulo">Gemelo digital del aula · Grupo 1, Sección 8 · PI3 UTEC</span>
        </div>
        <div className="reloj">
          <span className="hora">{reloj.hora}</span>
          <span>{reloj.fecha}</span>
          <span className={reloj.fueraDeHorario ? 'pastilla atencion' : 'pastilla'}>
            {reloj.fueraDeHorario ? 'Fuera de horario' : 'En horario'}
          </span>
          <span className={conectado ? 'pastilla bien' : 'pastilla critico'}>{conectado ? 'En vivo' : 'Reconectando…'}</span>
        </div>
        <div className="enlaces">
          <a href={grafana} target="_blank" rel="noreferrer">Históricos en Grafana ↗</a>
          <span className={supuestos.supuestos ? 'pastilla atencion' : 'pastilla bien'}
                title={supuestos.pendientes.map((p) => `${p.clave} = ${JSON.stringify(p.valor)}`).join('\n')}>
            {supuestos.supuestos} de {supuestos.total} datos del aula son supuestos
          </span>
        </div>
      </div>
      {fuente.simulado && (
        <div className="escenarios">
          <span className="etiqueta">Escenario:</span>
          {Object.entries(fuente.escenarios).map(([clave, descripcion]) => (
            <button key={clave} title={descripcion} className={fuente.escenario === clave ? 'activo' : ''}
                    onClick={() => ejecutar(`/api/demo/escenario/${clave}`)}>
              {clave}
            </button>
          ))}
          <span className="etiqueta separado">Velocidad:</span>
          {VELOCIDADES.map((v) => (
            <button key={v} className={reloj.velocidad === v ? 'activo' : ''} onClick={() => ejecutar(`/api/demo/velocidad/${v}`)}>
              ×{v}
            </button>
          ))}
          <button onClick={() => ejecutar('/api/demo/pausa')}>{reloj.pausado ? 'Reanudar' : 'Pausar'}</button>
          {error && <span className="error">{error}</span>}
        </div>
      )}
    </header>
  )
}
