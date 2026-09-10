import Panel from './Panel.jsx'
import { numero, horaCorta } from '../formato.js'

// Cada línea es un mensaje tal como lo publicaría un ESP32. Sirve para mostrar
// que el tablero no inventa nada: dibuja lo que llega por el tópico.
export default function FlujoMqtt({ mensajes }) {
  return (
    <Panel titulo="Mensajes de los nodos" requisito="RF-05">
      {mensajes.length === 0 ? (
        <p className="vacio">Todavía no llega ningún mensaje.</p>
      ) : (
        <ul className="lista flujo">
          {mensajes.map((mensaje) => (
            <li key={`${mensaje.topico}-${mensaje.seq}`}>
              <span className="hora-mensaje">{horaCorta(mensaje.ts)}</span>
              <span className="topico">{mensaje.topico}</span>
              <span className="valor-mensaje">
                {numero(mensaje.valor, Number.isInteger(mensaje.valor) ? 0 : 2)} {mensaje.unidad}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  )
}
