export const NOMBRES_DE_NIVEL = {
  nominal: 'Nominal',
  alerta: 'Alerta',
  critico: 'Crítico',
  desconocido: 'Sin datos',
}

export const TIPOS = {
  co2: { nombre: 'CO₂', icono: '◍' },
  audio: { nombre: 'Ruido', icono: '◠' },
  gas: { nombre: 'Gas / humo', icono: '△' },
  luz: { nombre: 'Luz', icono: '☼' },
  termico: { nombre: 'Ocupación', icono: '◉' },
  magnetico: { nombre: 'Puerta', icono: '▯' },
  ambiente: { nombre: 'Ambiente', icono: '≋' },
}

export function numero(valor, decimales = 0) {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return '—'
  if (typeof valor === 'boolean') return valor ? 'sí' : 'no'
  return Number(valor).toLocaleString('es-PE', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  })
}

export function decimalesDe(tipo) {
  return { ambiente: 1, audio: 1, gas: 2 }[tipo] ?? 0
}

export function hora(iso) {
  return iso ? iso.slice(11, 19) : '—'
}
