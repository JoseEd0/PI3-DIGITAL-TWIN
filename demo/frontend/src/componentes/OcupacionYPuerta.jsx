import Panel from './Panel.jsx'
import Chispa from './Chispa.jsx'
import { numero } from '../formato.js'

export default function OcupacionYPuerta({ resumen, series, eventos }) {
  const ultimoEvento = eventos[0]

  return (
    <Panel titulo="Ocupación y puerta" requisito="RF-03 · RF-04">
      <div className="trio">
        <div className="medida">
          <span className="etiqueta">Presencia</span>
          <div className="lectura compacta">
            <span className="valor">{resumen.presencia ? 'Ocupado' : 'Vacío'}</span>
          </div>
          <span className="etiqueta">
            {resumen.presencia
              ? `${numero(resumen.conteo)} personas estimadas (±2)`
              : `Vacío hace ${numero(resumen.minutosVacio)} min`}
          </span>
          <Chispa datos={series.conteo} color="var(--petroleo)" etiqueta="Conteo de personas" />
        </div>

        <div className="medida">
          <span className="etiqueta">Puerta</span>
          <div className="lectura compacta">
            <span className="valor">{resumen.puertaAbierta ? 'Abierta' : 'Cerrada'}</span>
          </div>
          <span className="etiqueta">Batería del nodo {numero(resumen.bateria)} %</span>
          {ultimoEvento && (
            <div className="detalle">
              <span>
                Último evento <b>{ultimoEvento.tipo}</b> a las {ultimoEvento.ts?.slice(11, 16)}
                {ultimoEvento.detalle ? `, ${ultimoEvento.detalle}` : ''}
              </span>
            </div>
          )}
        </div>
      </div>
    </Panel>
  )
}
