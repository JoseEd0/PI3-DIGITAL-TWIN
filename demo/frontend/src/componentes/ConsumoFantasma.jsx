import Panel from './Panel.jsx'
import { numero, soles } from '../formato.js'

const CARGAS = [
  ['iluminacion', 'Iluminación', 'var(--carga-iluminacion)'],
  ['computo', 'Cómputo', 'var(--carga-computo)'],
  ['otros', 'Otros', 'var(--carga-otros)'],
]

export default function ConsumoFantasma({ fantasma }) {
  const porCarga = fantasma.porCarga || {}
  const total = CARGAS.reduce((suma, [clave]) => suma + (porCarga[clave] || 0), 0)

  return (
    <Panel titulo="Consumo fantasma" requisito="RF-10">
      <div className="fantasma">
        <div className="titular">
          <div className="lectura">
            <span className="valor">{numero(fantasma.kwhFantasma, 2)}</span>
            <span className="unidad">kWh gastados con el aula vacía</span>
          </div>
          <div className="detalle">
            <span>Del consumo total <b>{numero(fantasma.porcentajeEvitable, 1)} %</b></span>
            <span>Equivale a <b>{soles(fantasma.soles)}</b></span>
            <span>y a <b>{numero(fantasma.kgCO2, 2)} kg CO₂</b></span>
          </div>
          <div className="detalle">
            <span>
              Se cuenta la energía que corre tras 15 minutos seguidos sin nadie adentro.
              Tarifa {soles(fantasma.tarifa)}/kWh y {numero(fantasma.factorDeEmision, 2)} kg CO₂/kWh,
              ambas por confirmar con Servicios Generales.
            </span>
          </div>
        </div>

        <div>
          <span className="etiqueta">Reparto por carga</span>
          <div className="barra-de-cargas" role="img"
            aria-label={CARGAS.map(([clave, texto]) => `${texto}: ${numero(porCarga[clave] || 0, 2)} kWh`).join('; ')}>
            {CARGAS.map(([clave, , color]) => {
              const valor = porCarga[clave] || 0
              const ancho = total > 0 ? (valor / total) * 100 : 0
              return ancho > 0 ? <i key={clave} style={{ width: `${ancho}%`, background: color }} /> : null
            })}
            {total === 0 && <i style={{ width: '100%', background: 'var(--panel-hundido)' }} />}
          </div>
          <div className="leyenda">
            {CARGAS.map(([clave, texto, color]) => (
              <span key={clave}>
                <i className="muestra-de-color" style={{ background: color }} />
                {texto} {numero(porCarga[clave] || 0, 2)} kWh
              </span>
            ))}
          </div>

          <div className="reparto">
            <div>
              <span className="etiqueta">Dentro del horario</span>
              <div className="lectura compacta">
                <span className="valor">{numero(fantasma.kwhEnHorario, 2)}</span>
                <span className="unidad">kWh</span>
              </div>
            </div>
            <div>
              <span className="etiqueta">Fuera del horario</span>
              <div className="lectura compacta">
                <span className="valor">{numero(fantasma.kwhFueraDeHorario, 2)}</span>
                <span className="unidad">kWh</span>
              </div>
            </div>
            <div>
              <span className="etiqueta">Consumo total medido</span>
              <div className="lectura compacta">
                <span className="valor">{numero(fantasma.kwhTotales, 2)}</span>
                <span className="unidad">kWh</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  )
}
