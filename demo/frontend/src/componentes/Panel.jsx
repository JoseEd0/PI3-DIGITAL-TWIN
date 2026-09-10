export default function Panel({ titulo, requisito, children, className = '' }) {
  return (
    <section className={`panel ${className}`.trim()}>
      <header>
        <h2>{titulo}</h2>
        {requisito && <span className="requisito" title="Requisito que demuestra este panel">{requisito}</span>}
      </header>
      <div className="cuerpo">{children}</div>
    </section>
  )
}
