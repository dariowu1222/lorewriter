import React from "react";

import ArcTimeline from "./ArcTimeline.jsx";
import EvalSummary from "./EvalSummary.jsx";
import NextStepPanel from "./NextStepPanel.jsx";
import RenderStatusCard from "./RenderStatusCard.jsx";
import RuleListCard from "./RuleListCard.jsx";
import StorySummaryCard from "./StorySummaryCard.jsx";
import TechnicalDebugPanel from "./TechnicalDebugPanel.jsx";
import WorldInfoCard from "./WorldInfoCard.jsx";

export default function OutputPanel({ output, loading }) {
  const data = output?.data || {};
  const storyboard = data.storyboard;
  const storyBible = storyboard?.story_bible;
  const rules = storyBible?.world_rules || data.rules || [];

  return (
    <aside className="output-panel">
      <div className="output-header">
        <h2>創作輸出</h2>
        {loading && <span className="status">Loading...</span>}
      </div>

      {output && (
        <div
          className={output.success ? "status status-ok" : "status status-error"}
        >
          <div>{output.message || output.error}</div>
          {!output.success && output.error && <small>{output.error}</small>}
        </div>
      )}

      {data.prompt && (
        <section className="creator-card">
          <h3>Prompt</h3>
          <textarea className="mono" rows={10} readOnly value={data.prompt} />
        </section>
      )}

      <StorySummaryCard storyboard={storyboard} />
      <RuleListCard rules={rules} />
      <WorldInfoCard storyBible={storyBible} />
      <ArcTimeline arcPlan={storyboard?.arc_plan} />
      <EvalSummary evalResult={data.eval_result} />
      <RenderStatusCard renderProject={data.render_project} />
      <NextStepPanel />
      <TechnicalDebugPanel output={output} />
    </aside>
  );
}
