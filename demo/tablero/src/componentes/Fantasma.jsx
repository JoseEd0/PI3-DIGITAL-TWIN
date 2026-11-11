import React from 'react'
import { numero } from '../formato.js'

// RA-08 / RF-10: el eje del proyecto. Estimado por proxy (no hay PZEM en la arquitectura oficial).
export default function Fantasma({ fantasma, derivados }) {
  return (
    <section className="panel fantasma">
      <h2>Consumo fantasma <span className="pastilla atencion">estimación</span></h2>
      <div className="cifras">
        <div><span className="cifra">{numero(fantasma.soles, 2)}</span><span>S/ evitables</span></div>
        <div><span className="cifra">{numero(fantasma.kwh, 2)}</span><span>kWh</span></div>
        <div><span className="cifra">{numero(fantasma.kgCo2, 2)}</span><span>kg de CO₂</span></div>
      </div>
      <p>Ahora: {fantasma.potenciaActualW > 0 ? `${numero(fantasma.potenciaActualW)} W desperdiciándose` : 'sin consumo evitable'} ·
        luces {derivados.luces_encendidas ? 'encendidas' : 'apagadas'} · aula {derivados.aula_vacia ? 'vacía' : 'ocupada'}</p>
      <p className="nota">{fantasma.episodios} episodio(s), {numero(fantasma.minutos)} min. {fantasma.metodo}.
        Tarifa {fantasma.tarifa} S/·kWh{fantasma.basadoEnSupuestos ? ' (valores supuestos hasta medir el aula)' : ''}.</p>
    </section>
  )
}
