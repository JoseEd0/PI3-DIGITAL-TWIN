import BarraSuperior from './componentes/BarraSuperior.jsx'
import Panel from './componentes/Panel.jsx'
import PlanoDelAula from './componentes/PlanoDelAula.jsx'
import Energia from './componentes/Energia.jsx'
import Ambiente from './componentes/Ambiente.jsx'
import OcupacionYPuerta from './componentes/OcupacionYPuerta.jsx'
import ConsumoFantasma from './componentes/ConsumoFantasma.jsx'
import Alertas from './componentes/Alertas.jsx'
import SaludDeNodos from './componentes/SaludDeNodos.jsx'
import FlujoMqtt from './componentes/FlujoMqtt.jsx'
import { useGemelo } from './useGemelo.js'

export default function App() {
  const { estado, conectado, series } = useGemelo()

  if (!estado) {
    return (
      <main className="aplicacion">
        <div className="aviso">
          <p>No hay datos del gemelo todavía.</p>
          <p>
            Levanta el servidor de la demo y recarga:
            <br />
            <code>cd demo/servidor &amp;&amp; .venv/bin/python -m campus_twin_demo</code>
          </p>
        </div>
      </main>
    )
  }

  const { resumen, umbrales, fantasma, alertas, alertasRecientes, salud, mensajes, eventos } = estado

  return (
    <main className="aplicacion">
      <BarraSuperior estado={estado} conectado={conectado} />

      <div className="rejilla">
        <Panel titulo="Laboratorio L-419" requisito="RF-07" className="hero">
          <PlanoDelAula resumen={resumen} salud={salud} alertas={alertas} />
        </Panel>

        <div className="columna">
          <Energia resumen={resumen} series={series} umbral={umbrales.consumoConAulaVacia} />
          <OcupacionYPuerta resumen={resumen} series={series} eventos={eventos} />
        </div>
      </div>

      <Ambiente resumen={resumen} series={series} umbralDeCo2={umbrales.co2} />

      <ConsumoFantasma fantasma={fantasma} />

      <div className="rejilla-inferior">
        <Alertas alertas={alertas} recientes={alertasRecientes} />
        <SaludDeNodos salud={salud} />
        <FlujoMqtt mensajes={mensajes} />
      </div>
    </main>
  )
}
