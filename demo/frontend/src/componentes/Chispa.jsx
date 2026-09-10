import { numero } from '../formato.js'

const ALTO = 30
const ANCHO = 100

/**
 * Línea de tendencia de una sola serie. El valor actual se lee en la cifra
 * grande de al lado, así que aquí no hay ejes ni etiquetas: solo la forma.
 */
export default function Chispa({ datos, color, umbral = null, etiqueta, decimales = 0 }) {
  const valores = datos.map((punto) => punto.valor).filter((v) => Number.isFinite(v))
  if (valores.length < 2) {
    return <svg className="chispa" role="img" aria-label={`${etiqueta}: sin datos suficientes`} />
  }

  const referencias = umbral === null ? valores : [...valores, umbral]
  const minimo = Math.min(...referencias)
  const maximo = Math.max(...referencias)
  const rango = maximo - minimo || 1
  const margen = rango * 0.12

  const enX = (indice) => (indice / (valores.length - 1)) * ANCHO
  const enY = (valor) => ALTO - ((valor - minimo + margen) / (rango + margen * 2)) * ALTO

  const puntos = valores.map((valor, indice) => `${enX(indice).toFixed(2)},${enY(valor).toFixed(2)}`)
  const linea = `M${puntos.join(' L')}`
  const area = `${linea} L${ANCHO},${ALTO} L0,${ALTO} Z`
  const ultimoX = enX(valores.length - 1)
  const ultimoY = enY(valores[valores.length - 1])

  const primero = valores[0]
  const ultimo = valores[valores.length - 1]
  const tendencia = ultimo > primero ? 'subiendo' : ultimo < primero ? 'bajando' : 'estable'

  return (
    <svg
      className="chispa"
      viewBox={`0 0 ${ANCHO} ${ALTO}`}
      preserveAspectRatio="none"
      role="img"
      aria-label={`${etiqueta}: ${tendencia}, de ${numero(primero, decimales)} a ${numero(ultimo, decimales)}`}
    >
      <path className="area" d={area} fill={color} />
      {umbral !== null && umbral >= minimo && umbral <= maximo && (
        <line className="umbral" x1="0" x2={ANCHO} y1={enY(umbral)} y2={enY(umbral)} vectorEffect="non-scaling-stroke" />
      )}
      <path className="linea" d={linea} stroke={color} vectorEffect="non-scaling-stroke" />
      {/* Un trazo de longitud cero con extremo redondo dibuja un punto que no
          se deforma aunque el eje X esté estirado. */}
      <line
        className="final"
        x1={ultimoX}
        x2={ultimoX}
        y1={ultimoY}
        y2={ultimoY}
        stroke={color}
        strokeWidth="7"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )
}
