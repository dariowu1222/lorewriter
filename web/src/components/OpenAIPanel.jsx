import React, { useState } from "react";

import { generateWithOpenAI } from "../api.js";

export default function OpenAIPanel({
  sharedState,
  fields,
  loading,
  setLoading,
  setOutput,
}) {
  const modelField = fields.find((field) => field.id === "model");
  const ignoreBudgetField = fields.find(
    (field) => field.id === "ignore_budget_guard",
  );
  const [model, setModel] = useState(modelField?.default || "gpt-4o-mini");
  const [ignoreBudgetGuard, setIgnoreBudgetGuard] = useState(
    Boolean(ignoreBudgetField?.default),
  );

  async function handleGenerate() {
    setLoading(true);
    try {
      const response = await generateWithOpenAI({
        sub_genre: sharedState.sub_genre,
        duration: sharedState.duration,
        model,
        enable_eval: sharedState.enable_eval,
        enable_auto_fix: sharedState.enable_auto_fix,
        export_render_input: sharedState.export_render_input,
        ignore_budget_guard: ignoreBudgetGuard,
        forbidden_words_text: sharedState.forbidden_words,
      });
      setOutput(response);
    } catch (error) {
      setOutput({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>API 自動模式 OpenAI</h2>
      <label className="field">
        <span>模型</span>
        <select value={model} onChange={(event) => setModel(event.target.value)}>
          {(modelField?.options || ["gpt-4o-mini", "gpt-4o"]).map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
      <label className="inline-field">
        <input
          type="checkbox"
          checked={ignoreBudgetGuard}
          onChange={(event) => setIgnoreBudgetGuard(event.target.checked)}
        />
        <span>忽略成本保護</span>
      </label>
      <button type="button" onClick={handleGenerate} disabled={loading}>
        API 生成
      </button>
    </section>
  );
}
