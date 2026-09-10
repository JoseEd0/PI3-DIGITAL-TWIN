import Panel from './Panel.jsx'
import { numero } from '../formato.js'

function estadoDelNodo(fila) {
  if (fila.ultimaMuestra === null) return ['apagado', 'Sin datos']
  if (fila.caido) return ['critico', 'Caído']
  if (fila.muestrasPerdidas > 1) return ['atencion', 'Perdiendo muestras']
  return ['bien', 'En línea']
}

export default function SaludDeNodos({ salud }) {
  return (
    <Panel titulo="Salud de los nodos" requisito="RF-13">
      <div className="tabla-desplazable">
      <table className="salud">
        <thead>
          <tr>
            <th scope="col">Nodo</th>
            <th scope="col">Estado</th>
            <th scope="col" className="numero">Señal</th>
            <th scope="col" className="numero">Perdidas</th>
          </tr>
        </thead>
        <tbody>
          {salud.map((fila) => {
            const [clase, texto] = estadoDelNodo(fila)
            return (
              <tr key={fila.nodo}>
                <td>
                  {fila.etiqueta}
                  <br />
                  <span className="requisito">{fila.requisito}</span>
                </td>
                <td><span className={`marca ${clase}`}>{texto}</span></td>
                <td className="numero">{fila.senal === null ? '—' : `${numero(fila.senal)} dBm`}</td>
                <td className="numero">{numero(fila.muestrasPerdidas, 2)} %</td>
              </tr>
            )
          })}
        </tbody>
      </table>
      </div>
    </Panel>
  )
}
