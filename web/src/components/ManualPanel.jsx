import { useState } from "react";

import { generateManualPrompt, parseManualResponse } from "../api.js";

function fieldDefault(fields, id, fallback) {
  return fields.find((field) => field.id === id)?.default || fallback;
}

export default function ManualPanel({
  sharedState,
  fields,
  loading,
  setLoading,
  setOutput,
}) {
  const [prompt, setPrompt] = useState("");
  const [manualResponse, setManualResponse] = useState("");
  const [promptPath] = useState(
    fieldDefault(fields, "manual_prompt_output", "output/manual_prompt.txt"),
  );
  const [responsePath] = useState(
    fieldDefault(fields, "manual_response_input", "output/manual_response.json"),
  );

  async function handlePrompt() {
    setLoading(true);
    try {
      const response = await generateManualPrompt({
        sub_genre: sharedState.sub_genre,
        duration: sharedState.duration,
        forbidden_words_text: sharedState.forbidden_words,
      });
      setPrompt(response.data.prompt);
      setOutput(response);
    } catch (error) {
      setOutput({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleParse() {
    setLoading(true);
    try {
      const response = await parseManualResponse({
        manual_response_text: manualResponse,
        enable_eval: sharedState.enable_eval,
        enable_auto_fix: sharedState.enable_auto_fix,
        export_render_input: sharedState.export_render_input,
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
      <h2>省錢模式 Manual</h2>
      <div className="path-row">
        <span>{promptPath}</span>
        <span>{responsePath}</span>
      </div>
      <button type="button" onClick={handlePrompt} disabled={loading}>
        產生 Prompt
      </button>
      <textarea
        className="mono"
        value={prompt}
        rows={8}
        readOnly
        placeholder="Prompt 會顯示在這裡"
      />
      <button
        type="button"
        onClick={() => navigator.clipboard?.writeText(prompt)}
        disabled={!prompt}
      >
        複製 Prompt
      </button>
      <textarea
        className="mono"
        value={manualResponse}
        rows={10}
        onChange={(event) => setManualResponse(event.target.value)}
        placeholder="貼上 ChatGPT / Claude / Gemini 回傳的 JSON"
      />
      <button type="button" onClick={handleParse} disabled={loading}>
        解析並評估
      </button>
    </section>
  );
}
