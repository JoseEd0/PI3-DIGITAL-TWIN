import React from 'react'
import { NOMBRES_DE_NIVEL, numero } from '../formato.js'

// Mínimo 2 de la pauta EC3: estado del salón frente a cada requisito de alto nivel.
export default function Requisitos({ requisitos, elegido, alElegir }) {
  return (
    <section className="panel requisitos">
      <h2>Condición del salón por requisito</h2>
      <ul>
        {requisitos.map((r) => (
          <li key={r.ra}>
            <button className={`requisito ${r.nivel} ${elegido === r.ra ? 'elegido' : ''}`} onClick={() => alElegir(r.ra)}>
              <span className={`semaforo ${r.nivel}`} aria-hidden="true" />
              <span className="ra-id">{r.ra}</span>
              <span className="ra-nombre">{r.nombre}</span>
              <span className="ra-valor">
                {typeof r.valor === 'number' ? numero(r.valor, Number.isInteger(r.valor) ? 0 : 1) : ''} {r.unidad}
              </span>
              <span className={`nivel ${r.nivel}`}>{NOMBRES_DE_NIVEL[r.nivel]}</span>
            </button>
          </li>
        ))}
      </ul>
      <p className="nota">Toca un requisito para ver sus causas, efectos y recomendaciones.</p>
    </section>
  )
}
