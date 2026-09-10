import { useEffect, useRef, useState } from 'react'

// Series que el tablero dibuja. Se siembran una vez con el histórico del
// servidor y después crecen con cada evento del flujo.
export const SERIES = [
  { clave: 'potencia', nodo: 'energia', magnitud: 'potencia' },
  { clave: 'co2', nodo: 'ambiental', magnitud: 'co2' },
  { clave: 'temperatura', nodo: 'ambiental', magnitud: 'temperatura' },
  { clave: 'iluminancia', nodo: 'ambiental', magnitud: 'iluminancia' },
  { clave: 'conteo', nodo: 'ocupacion-puerta', magnitud: 'conteo' },
]

const MAXIMO_DE_PUNTOS = 180
const REINTENTO_MS = 3000

function agregar(serie, ts, valor) {
  if (valor === null || valor === undefined) return serie
  if (serie.length && serie[serie.length - 1].ts === ts) return serie
  const siguiente = serie.length >= MAXIMO_DE_PUNTOS ? serie.slice(1) : serie.slice()
  siguiente.push({ ts, valor })
  return siguiente
}

/** Mantiene el estado del gemelo al día: flujo SSE y, si falla, consultas. */
export function useGemelo() {
  const [estado, setEstado] = useState(null)
  const [conectado, setConectado] = useState(false)
  const [series, setSeries] = useState(() => Object.fromEntries(SERIES.map((s) => [s.clave, []])))
  const seriesRef = useRef(series)

  useEffect(() => {
    let cancelado = false

    // Semilla: sin esto los gráficos arrancan vacíos aunque el simulador lleve
    // rato corriendo.
    Promise.all(
      SERIES.map(async ({ clave, nodo, magnitud }) => {
        try {
          const respuesta = await fetch(`/api/historico?nodo=${nodo}&magnitud=${magnitud}&limite=120`)
          if (!respuesta.ok) return [clave, []]
          const datos = await respuesta.json()
          return [clave, datos.muestras.map((m) => ({ ts: m.ts, valor: m.valor }))]
        } catch {
          return [clave, []]
        }
      }),
    ).then((entradas) => {
      if (cancelado) return
      const sembradas = Object.fromEntries(entradas)
      seriesRef.current = { ...seriesRef.current, ...sembradas }
      setSeries(seriesRef.current)
    })

    return () => {
      cancelado = true
    }
  }, [])

  useEffect(() => {
    let fuente = null
    let reintento = null
    let encuesta = null

    const alRecibir = (instantanea) => {
      setEstado(instantanea)
      setConectado(true)
      const ts = instantanea.reloj?.ts
      const resumen = instantanea.resumen || {}
      const siguiente = { ...seriesRef.current }
      for (const { clave } of SERIES) {
        siguiente[clave] = agregar(siguiente[clave] || [], ts, resumen[clave])
      }
      seriesRef.current = siguiente
      setSeries(siguiente)
    }

    const consultar = async () => {
      try {
        const respuesta = await fetch('/api/estado')
        if (!respuesta.ok) throw new Error(respuesta.statusText)
        alRecibir(await respuesta.json())
      } catch {
        setConectado(false)
      }
    }

    const conectar = () => {
      fuente = new EventSource('/api/stream')
      fuente.onmessage = (evento) => alRecibir(JSON.parse(evento.data))
      fuente.onerror = () => {
        setConectado(false)
        fuente.close()
        // El navegador reintenta solo, pero si el servidor está caído conviene
        // seguir consultando para no dejar el tablero congelado sin avisar.
        if (!encuesta) encuesta = setInterval(consultar, REINTENTO_MS)
        reintento = setTimeout(() => {
          if (encuesta) {
            clearInterval(encuesta)
            encuesta = null
          }
          conectar()
        }, REINTENTO_MS)
      }
    }

    consultar()
    conectar()

    return () => {
      if (fuente) fuente.close()
      if (reintento) clearTimeout(reintento)
      if (encuesta) clearInterval(encuesta)
    }
  }, [])

  return { estado, conectado, series }
}

/** Envía una orden de demostración al servidor (escenario, velocidad, pausa). */
export async function ordenar(ruta) {
  try {
    const respuesta = await fetch(`/api/demo/${ruta}`, { method: 'POST' })
    return respuesta.ok
  } catch {
    return false
  }
}
