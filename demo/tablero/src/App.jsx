import React, { useState } from 'react'
import { useGemelo } from './useGemelo.js'
import BarraSuperior from './componentes/BarraSuperior.jsx'
import Requisitos from './componentes/Requisitos.jsx'
import Diagnostico from './componentes/Diagnostico.jsx'
import Mediciones from './componentes/Mediciones.jsx'
import Plano from './componentes/Plano.jsx'
import Fantasma from './componentes/Fantasma.jsx'
import Bitacora from './componentes/Bitacora.jsx'
import Salud from './componentes/Salud.jsx'

// Elige el RA a mostrar: el que el usuario tocó o, si no, el más grave que esté violado.
function raPorDefecto(requisitos) {
  const orden = { critico: 2, alerta: 1 }
  const violados = requisitos.filter((r) => orden[r.nivel]).sort((a, b) => orden[b.nivel] - orden[a.nivel])
  return violados[0]?.ra ?? 'RA-03'
}

export default function App() {
  const { estado, conectado } = useGemelo()
  const [raElegido, setRaElegido] = useState(null)
  const [nodoElegido, setNodoElegido] = useState(null)

  if (!estado) {
    return <main className="cargando">Conectando con el gemelo del L-419…</main>
  }
  const ra = raElegido ?? raPorDefecto(estado.requisitos)

  return (
    <main className="tablero">
      <BarraSuperior estado={estado} conectado={conectado} />
      <section className="fila fila-principal">
        <Requisitos requisitos={estado.requisitos} elegido={ra} alElegir={setRaElegido} />
        <Diagnostico ra={ra} requisito={estado.requisitos.find((r) => r.ra === ra)} />
      </section>
      <Mediciones mediciones={estado.mediciones} salud={estado.salud} elegido={nodoElegido} alElegir={setNodoElegido} />
      <section className="fila">
        <Plano estado={estado} elegido={nodoElegido} alElegir={setNodoElegido} />
        <Fantasma fantasma={estado.fantasma} derivados={estado.derivados} />
        <Salud salud={estado.salud} gatewayEnLinea={estado.gatewayEnLinea} />
      </section>
      <Bitacora eventosRecientes={estado.eventos} />
    </main>
  )
}
