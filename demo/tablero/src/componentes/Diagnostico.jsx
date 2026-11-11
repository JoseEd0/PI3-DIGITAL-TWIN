import React, { useEffect, useState } from 'react'
import { leer } from '../useGemelo.js'
import { NOMBRES_DE_NIVEL } from '../formato.js'
import GrafoCausal from './GrafoCausal.jsx'

const REFRESCO_MS = 2000

function ListaDeCausas({ titulo, causas, clase }) {
  if (!causas.length) return null
  return (
    <div className={`causas ${clase}`}>
      <h4>{titulo}</h4>
      <ul>
        {causas.map((c) => (
          <li key={c.id}>
            {c.texto}
            {c.observado && <span className="marca">medido</span>}
          </li>
        ))}
      </ul>
    </div>
  )
}

// Mínimo 3 de la pauta EC3: causas y efectos de cada violación, con recomendaciones.
export default function Diagnostico({ ra, requisito }) {
  const [grafo, setGrafo] = useState(null)

  useEffect(() => {
    let vigente = true
    const actualizar = () => leer(`/api/grafos/${ra}`).then((g) => vigente && setGrafo(g)).catch(() => {})
    actualizar()
    const intervalo = setInterval(actualizar, REFRESCO_MS)
    return () => {
      vigente = false
      clearInterval(intervalo)
    }
  }, [ra])

  if (!grafo || !requisito || grafo.ra !== ra) return <section className="panel diagnostico">Cargando {ra}…</section>
  const d = grafo.diagnostico
  const violado = requisito.nivel === 'alerta' || requisito.nivel === 'critico'

  return (
    <section className={`panel diagnostico ${requisito.nivel}`}>
      <header className="diagnostico-cabecera">
        <div>
          <h2>{ra} · {requisito.nombre}</h2>
          <p className="mensaje">{requisito.mensaje}</p>
          <p className="norma">Umbral: {requisito.norma} ({requisito.origenUmbral === 'docente' ? 'mismo umbral que el nodo del docente' : 'norma'}) · deriva de {requisito.necesidad}</p>
        </div>
        <span className={`nivel grande ${requisito.nivel}`}>{NOMBRES_DE_NIVEL[requisito.nivel]}</span>
      </header>
      <div className="diagnostico-cuerpo">
        <div className="explicacion">
          {violado ? (
            <>
              <ListaDeCausas titulo="Causas confirmadas" causas={d.causasConfirmadas} clase="confirmadas" />
              <ListaDeCausas titulo="Causas sospechosas (por orden de probabilidad)" causas={d.causasSospechosas} clase="sospechosas" />
              <ListaDeCausas titulo="Descartadas por las mediciones" causas={d.causasDescartadas} clase="descartadas" />
              <div className="efectos">
                <h4>Consecuencias esperadas</h4>
                <ul>{d.efectosEsperados.map((e) => <li key={e.id}>{e.texto}</li>)}</ul>
              </div>
              <div className="recomendaciones">
                <h4>Qué hacer</h4>
                <ol>{d.recomendaciones.map((r) => <li key={r}>{r}</li>)}</ol>
              </div>
            </>
          ) : (
            <p className="tranquilo">
              Sin violación: el grafo de la derecha muestra qué se vigila. Las causas descartadas por las mediciones
              aparecen en gris.
            </p>
          )}
        </div>
        <GrafoCausal grafo={grafo} />
      </div>
    </section>
  )
}
