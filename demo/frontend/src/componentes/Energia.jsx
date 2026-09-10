import Panel from './Panel.jsx'
import Chispa from './Chispa.jsx'
import { numero } from '../formato.js'

export default function Energia({ resumen, series, umbral }) {
  const conAulaVacia = !resumen.presencia && resumen.potencia > umbral

  return (
    <Panel titulo="Energía del laboratorio" requisito="RF-01 · RF-12">
      <div className="lectura">
        <span className="valor">{numero(resumen.potencia)}</span>
        <span className="unidad">W ahora</span>
        {conAulaVacia && <span className="marca atencion" style={{ marginLeft: 'auto' }}>Sin nadie adentro</span>}
      </div>
      <Chispa datos={series.potencia} color="var(--cobre)" etiqueta="Potencia" />
      <div className="detalle">
        <span>Energía acumulada <b>{numero(resumen.energia, 3)} kWh</b></span>
        <span>Tensión <b>{numero(resumen.tension, 1)} V</b></span>
        <span>Corriente <b>{numero(resumen.corriente, 2)} A</b></span>
        <span>Factor de potencia <b>{numero(resumen.factorDePotencia, 2)}</b></span>
      </div>
      <div className="detalle">
        <span>Luminarias <b>{resumen.lucesEncendidas ? 'encendidas' : 'apagadas'}</b></span>
        <span>Proyector <b>{resumen.proyectorEncendido ? 'encendido' : 'apagado'}</b></span>
        <span>PC encendidos <b>{numero(resumen.pcsEncendidos)}</b></span>
        <span>Aire <b>{resumen.aireEncendido ? 'encendido' : 'apagado'}</b></span>
      </div>
    </Panel>
  )
}
