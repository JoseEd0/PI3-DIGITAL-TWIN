import React from 'react'
import { TIPOS, numero } from '../formato.js'

// RA-10 / RF-13: si el gemelo realmente está viendo el aula.
export default function Salud({ salud, gatewayEnLinea }) {
  return (
    <section className="panel salud">
      <h2>Salud del sistema</h2>
      <p className={gatewayEnLinea === false ? 'gateway critico' : 'gateway'}>
        Gateway ESP32: {gatewayEnLinea === null ? 'sin estado aún' : gatewayEnLinea ? 'en línea' : 'DESCONECTADO'}
      </p>
      <table>
        <thead><tr><th>Nodo</th><th>Último dato</th><th>Tolerancia</th><th>Perdidos</th></tr></thead>
        <tbody>
          {salud.map((s) => (
            <tr key={s.nodo} className={s.caido ? 'caido' : s.falla ? 'falla' : ''}>
              <td>{s.nodo} · {TIPOS[s.tipo].nombre}</td>
              <td>{s.segundosSinDatos === null ? '—' : `hace ${numero(s.segundosSinDatos)} s`}</td>
              <td>{numero(s.toleranciaS)} s</td>
              <td>{s.perdidos ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
