import Panel from './Panel.jsx'
import Chispa from './Chispa.jsx'
import { numero, severidadDeCo2 } from '../formato.js'

export default function Ambiente({ resumen, series, umbralDeCo2 }) {
  const estadoDelCo2 = severidadDeCo2(resumen.co2, umbralDeCo2)

  return (
    <Panel titulo="Ambiente" requisito="RF-02">
      <div className="trio">
        <div className="medida">
          <div className="cabecera">
            <span className="etiqueta">CO₂</span>
            {estadoDelCo2 !== 'bien' && (
              <span className={`marca ${estadoDelCo2}`}>
                {estadoDelCo2 === 'critico' ? 'Muy alto' : 'Sobre el umbral'}
              </span>
            )}
          </div>
          <div className="lectura compacta">
            <span className="valor">{numero(resumen.co2)}</span>
            <span className="unidad">ppm</span>
          </div>
          <Chispa datos={series.co2} color="var(--petroleo)" umbral={umbralDeCo2} etiqueta="CO₂" />
          <span className="etiqueta">Umbral {numero(umbralDeCo2)} ppm</span>
        </div>

        <div className="medida">
          <span className="etiqueta">Temperatura</span>
          <div className="lectura compacta">
            <span className="valor">{numero(resumen.temperatura, 1)}</span>
            <span className="unidad">°C</span>
          </div>
          <Chispa datos={series.temperatura} color="var(--petroleo)" etiqueta="Temperatura" decimales={1} />
          <span className="etiqueta">Humedad {numero(resumen.humedad)} %HR</span>
        </div>

        <div className="medida">
          <span className="etiqueta">Iluminancia</span>
          <div className="lectura compacta">
            <span className="valor">{numero(resumen.iluminancia)}</span>
            <span className="unidad">lx</span>
          </div>
          <Chispa datos={series.iluminancia} color="var(--cobre)" etiqueta="Iluminancia" />
          <span className="etiqueta">
            {resumen.lucesEncendidas ? 'Luminarias encendidas' : 'Solo luz natural'}
          </span>
        </div>
      </div>
    </Panel>
  )
}
