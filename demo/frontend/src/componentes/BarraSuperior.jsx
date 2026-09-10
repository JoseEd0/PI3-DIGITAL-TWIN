import { ordenar } from '../useGemelo.js'

const VELOCIDADES = [1, 60, 120, 240]

const ESCENARIOS_VISIBLES = [
  ['clase', 'Entra un grupo'],
  ['vacio-con-luces', 'Se van y dejan luces'],
  ['apertura-fuera-de-horario', 'Abren de madrugada'],
  ['caida-de-nodo', 'Se cae un nodo'],
  ['senal-debil', 'Señal débil'],
  ['restablecer', 'Volver al guion'],
]

export default function BarraSuperior({ estado, conectado }) {
  const reloj = estado?.reloj
  const escenario = estado?.escenario

  return (
    <header className="panel barra">
      <div className="identidad">
        <h1>Campus Twin · laboratorio L-419</h1>
        <p>Gemelo simulado. Los sensores llegan en la semana 6.</p>
      </div>

      <div className="reloj">
        <div>
          <div className="hora">{reloj?.hora ?? '--:--:--'}</div>
          <div className="fecha">
            {reloj?.fecha ?? ''} · hora del laboratorio simulado
          </div>
        </div>
        <div className="jornada">
          {reloj?.dentroDeHorario ? 'Dentro del horario' : 'Fuera del horario'}
          <br />
          {reloj ? `${reloj.horarioOficial[0]}:00 a ${reloj.horarioOficial[1]}:00` : ''}
        </div>
      </div>

      <div className="mandos">
        <span className="enlace-estado">
          <span className={conectado ? 'punto' : 'punto sin-conexion'} />
          {conectado ? 'Datos en vivo' : 'Sin conexión'}
        </span>

        <div className="grupo-de-mandos" role="group" aria-label="Velocidad del día simulado">
          {VELOCIDADES.map((velocidad) => (
            <button
              key={velocidad}
              type="button"
              className="mando"
              aria-pressed={reloj?.velocidad === velocidad}
              onClick={() => ordenar(`velocidad/${velocidad}`)}
            >
              {velocidad === 1 ? 'Tiempo real' : `${velocidad}×`}
            </button>
          ))}
        </div>

        <button
          type="button"
          className="mando"
          aria-pressed={reloj?.pausado === true}
          onClick={() => ordenar('pausa')}
        >
          {reloj?.pausado ? 'Reanudar' : 'Pausar'}
        </button>

        <div className="grupo-de-mandos" role="group" aria-label="Escenarios de demostración">
          {ESCENARIOS_VISIBLES.map(([clave, texto]) => (
            <button
              key={clave}
              type="button"
              className="mando"
              aria-pressed={escenario === clave}
              onClick={() => ordenar(`escenario/${clave}`)}
            >
              {texto}
            </button>
          ))}
        </div>
      </div>
    </header>
  )
}
