import Panel from './Panel.jsx'

export default function Alertas({ alertas, recientes }) {
  return (
    <Panel titulo="Alertas" requisito="RF-08">
      {alertas.length === 0 ? (
        <p className="vacio">Nada que atender. Las reglas siguen evaluándose cada medio segundo.</p>
      ) : (
        <ul className="lista">
          {alertas.map((alerta) => (
            <li key={alerta.codigo} className={`alerta ${alerta.severidad}`}>
              <span className={`marca ${alerta.severidad === 'critica' ? 'critico' : alerta.severidad}`}>
                {alerta.severidad === 'critica' ? 'Crítica' : 'Atención'}
              </span>
              <span>
                <span className="titulo">{alerta.titulo}</span>
                <span className="detalle-de-alerta">{alerta.detalle}</span>
              </span>
              <span className="requisito">{alerta.requisito}</span>
            </li>
          ))}
        </ul>
      )}

      {recientes.length > 0 && (
        <div className="detalle">
          <span>
            Últimas en dispararse: {recientes.slice(0, 3).map((a) => `${a.titulo} (${a.ts.slice(11, 16)})`).join(', ')}
          </span>
        </div>
      )}
    </Panel>
  )
}
