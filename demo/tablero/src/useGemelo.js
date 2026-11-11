import { useEffect, useState } from 'react'

const REINTENTO_MS = 3000

// Instantánea del servicio por Server-Sent Events; si el flujo se corta, reintenta solo.
export function useGemelo() {
  const [estado, setEstado] = useState(null)
  const [conectado, setConectado] = useState(false)

  useEffect(() => {
    let fuente
    let temporizador
    const conectar = () => {
      fuente = new EventSource('/api/stream')
      fuente.onmessage = (e) => {
        setEstado(JSON.parse(e.data))
        setConectado(true)
      }
      fuente.onerror = () => {
        setConectado(false)
        fuente.close()
        temporizador = setTimeout(conectar, REINTENTO_MS)
      }
    }
    conectar()
    return () => {
      clearTimeout(temporizador)
      fuente?.close()
    }
  }, [])

  return { estado, conectado }
}

export async function enviar(ruta) {
  const respuesta = await fetch(ruta, { method: 'POST' })
  if (!respuesta.ok) throw new Error((await respuesta.json()).detail ?? respuesta.statusText)
  return respuesta.json()
}

export async function leer(ruta) {
  const respuesta = await fetch(ruta)
  if (!respuesta.ok) throw new Error(respuesta.statusText)
  return respuesta.json()
}
