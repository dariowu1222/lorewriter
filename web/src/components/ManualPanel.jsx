import React from "react";

import { generateManualPrompt, parseManualResponse } from "../api.js";

function creatorPayload(sharedState) {
  return {
    sub_genre: sharedState.sub_genre,
    duration: sharedState.duration,
    generated_rules: sharedState.generated_rules,
    world_setting: sharedState.world_setting,
    horror_style: sharedState.horror_style,
    pacing_style: sharedState.pacing_style,
    ending_style: sharedState.ending_style,
    protagonist_type: sharedState.protagonist_type,
    object_focus: sharedState.object_focus,
    visual_style: sharedState.visual_style,
    forbidden_words_text: sharedState.forbidden_words,
  };
}

export default function ManualPanel({
  sharedState,
  onSharedStateChange,
  loading,
  setLoading,
  setOutput,
}) {
  async function handlePrompt() {
    setLoading(true);
    try {
      const response = await generateManualPrompt(creatorPayload(sharedState));
      onSharedStateChange({ manual_prompt_text: response.data.prompt });
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
        ...creatorPayload(sharedState),
        manual_response_text: sharedState.manual_response_text,
        enable_eval: sharedState.enable_eval,
        enable_auto_fix: sharedState.enable_auto_fix,
        export_render_input: sharedState.export_render_input,
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
      <p className="panel-note">
        產生 prompt，貼到 ChatGPT / Claude / Gemini，再把 JSON 回覆貼回來。
      </p>
      <button type="button" onClick={handlePrompt} disabled={loading}>
        產生 Prompt
      </button>
      <textarea
        className="mono"
        value={sharedState.manual_prompt_text}
        rows={9}
        readOnly
        placeholder="Prompt 會顯示在這裡"
      />
      <button
        type="button"
        className="secondary-button"
        onClick={() => navigator.clipboard?.writeText(sharedState.manual_prompt_text)}
        disabled={!sharedState.manual_prompt_text}
      >
        複製 Prompt
      </button>
      <textarea
        className="mono"
        value={sharedState.manual_response_text}
        rows={10}
        onChange={(event) =>
          onSharedStateChange({ manual_response_text: event.target.value })
        }
        placeholder="貼上模型回傳的 storyboard JSON"
      />
      <button type="button" onClick={handleParse} disabled={loading}>
        解析並評估
      </button>
    </section>
  );
}
