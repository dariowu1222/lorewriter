function JsonBlock({ title, value }) {
  if (value === undefined || value === null) {
    return null;
  }

  return (
    <section className="json-block">
      <h3>{title}</h3>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </section>
  );
}

export default function OutputPanel({ output, loading }) {
  const data = output?.data || {};

  return (
    <aside className="output-panel">
      <div className="output-header">
        <h2>輸出</h2>
        {loading && <span className="status">Loading...</span>}
      </div>
      {output && (
        <div
          className={output.success ? "status status-ok" : "status status-error"}
        >
          {output.message || output.error}
        </div>
      )}
      <JsonBlock title="Storyboard" value={data.storyboard} />
      <JsonBlock title="Eval Result" value={data.eval_result} />
      <JsonBlock title="Render Project" value={data.render_project} />
      <JsonBlock title="Estimated Cost" value={data.estimated_cost} />
      {data.prompt && (
        <section className="json-block">
          <h3>Prompt</h3>
          <pre>{data.prompt}</pre>
        </section>
      )}
    </aside>
  );
}
