import React, { useState } from "react";

export default function RenderStatusCard({ renderProject }) {
  const [expanded, setExpanded] = useState(false);
  if (!renderProject) {
    return null;
  }

  return (
    <section className="creator-card">
      <div className="section-heading">
        <h3>Render 狀態</h3>
        <button
          type="button"
          className="secondary-button"
          onClick={() => setExpanded((value) => !value)}
        >
          {expanded ? "收合 Render JSON" : "展開 Render JSON"}
        </button>
      </div>
      <dl className="summary-grid">
        <div>
          <dt>場景數</dt>
          <dd>{renderProject.scenes?.length || 0}</dd>
        </div>
        <div>
          <dt>總時長</dt>
          <dd>{renderProject.total_duration_sec || 0} 秒</dd>
        </div>
        <div>
          <dt>狀態</dt>
          <dd>{renderProject.scenes?.length ? "ready" : "not ready"}</dd>
        </div>
        <div>
          <dt>視覺風格</dt>
          <dd>{renderProject.visual_theme || "未設定"}</dd>
        </div>
      </dl>
      {expanded && <pre>{JSON.stringify(renderProject, null, 2)}</pre>}
    </section>
  );
}
