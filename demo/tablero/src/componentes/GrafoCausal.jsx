import React, { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'

// Colores por valor SymCure: V verdadero, S sospechoso, F falso (descartado), D desconocido.
const ESTILO_POR_VALOR = {
  V: { fondo: '#f4c7c3', borde: '#b3271e' },
  S: { fondo: '#f7e2b5', borde: '#a06a12' },
  F: { fondo: '#e6e8ea', borde: '#9aa3a8' },
  D: { fondo: '#ffffff', borde: '#77878f' },
}

function elementos(grafo) {
  const valores = grafo.diagnostico.valores
  const nodos = grafo.nodos.map((n) => {
    const estilo = ESTILO_POR_VALOR[valores[n.id] ?? 'D']
    return {
      data: {
        id: n.id,
        etiqueta: `${n.texto}\n[${n.entrada}-${n.salida}]${n.observable ? ' ●' : ''}`,
        fondo: estilo.fondo,
        borde: estilo.borde,
        ancho: n.id === grafo.central ? 4 : n.observable ? 2.5 : 1,
        linea: n.observable ? 'solid' : 'dashed',
      },
    }
  })
  const aristas = grafo.aristas.map(([causa, efecto]) => ({ data: { id: `${causa}->${efecto}`, source: causa, target: efecto } }))
  return [...nodos, ...aristas]
}

export default function GrafoCausal({ grafo }) {
  const contenedor = useRef(null)
  const instancia = useRef(null)

  useEffect(() => {
    instancia.current = cytoscape({
      container: contenedor.current,
      elements: elementos(grafo),
      layout: { name: 'breadthfirst', directed: true, spacingFactor: 1.05, padding: 8 },
      userZoomingEnabled: true,
      style: [
        {
          selector: 'node',
          style: {
            shape: 'round-rectangle', label: 'data(etiqueta)', 'text-wrap': 'wrap', 'text-max-width': 130,
            'font-size': 9, 'text-valign': 'center', width: 140, height: 46,
            'background-color': 'data(fondo)', 'border-color': 'data(borde)', 'border-width': 'data(ancho)',
            'border-style': 'data(linea)', color: '#16232b',
          },
        },
        { selector: 'edge', style: { width: 1.2, 'line-color': '#8a979e', 'target-arrow-color': '#8a979e',
                                     'target-arrow-shape': 'triangle', 'curve-style': 'bezier' } },
      ],
    })
    return () => instancia.current?.destroy()
  }, [grafo.ra])

  // Solo se recolorea al cambiar los valores, sin rehacer el layout (el grafo no salta).
  useEffect(() => {
    const cy = instancia.current
    if (!cy) return
    for (const elemento of elementos(grafo)) {
      if (elemento.data.source) continue
      cy.getElementById(elemento.data.id).data(elemento.data)
    }
  }, [grafo])

  return (
    <figure className="grafo">
      <div ref={contenedor} className="lienzo-grafo" />
      <figcaption>
        <span className="muestra v" /> verdadero <span className="muestra s" /> sospechoso
        <span className="muestra f" /> descartado <span className="muestra d" /> desconocido · ● medido por un sensor,
        borde punteado = inferido · lógica SymCure [entrada-salida]
      </figcaption>
    </figure>
  )
}
