import React, { useState } from "react";

function metadata(output) {
  const data = output?.data || {};
  const storyboard = data.storyboard || {};
  const evalResult = data.eval_result?.after_fix || data.eval_result || {};
  const renderProject = data.render_project || {};

  return {
    estimated_cost: data.estimated_cost || null,
    generation_mode:
      evalResult.generation_mode_check?.stats?.generation_mode || "unknown",
    model: storyboard.model || "unknown",
    unresolved_foreshadow_count:
      evalResult.story_memory_check?.stats?.unresolved_foreshadow_count || 0,
    render_scene_count: renderProject.scenes?.length || 0,
  };
}

export default function TechnicalDebugPanel({ output }) {
  const [expanded, setExpanded] = useState(false);
  if (!output) {
    return null;
  }

  return (
    <section className="creator-card">
      <button
        type="button"
        className="secondary-button"
        onClick={() => setExpanded((value) => !value)}
      >
        {expanded ? "收合技術資訊" : "展開技術 JSON"}
      </button>
      {expanded && (
        <>
          <pre>{JSON.stringify(metadata(output), null, 2)}</pre>
          <pre>{JSON.stringify(output, null, 2)}</pre>
        </>
      )}
    </section>
  );
}
