// Formato de números para lecturas que cambian dos veces por segundo: siempre
// el mismo número de decimales, para que la cifra no cambie de ancho ni salte.

export function numero(valor, decimales = 0) {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return '—'
  return Number(valor).toLocaleString('es-PE', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  })
}

export function soles(valor) {
  return `S/ ${numero(valor, 2)}`
}

export function horaCorta(iso) {
  if (!iso) return '—'
  return iso.slice(11, 19)
}

export function severidadDeCo2(co2, umbral) {
  if (co2 >= umbral * 1.4) return 'critico'
  if (co2 >= umbral) return 'atencion'
  return 'bien'
}
