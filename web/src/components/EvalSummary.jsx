import React from "react";

import { generateManualEvalPrompt, importManualEval } from "../api.js";

function finalEval(evalResult) {
  if (!evalResult) {
    return null;
  }
  return evalResult.after_fix || evalResult;
}

function statusLine(ok, successText, warningText) {
  return ok ? `✅ ${successText}` : `⚠ ${warningText}`;
}

function localEvalLines(result) {
  if (!result) {
    return ["尚未啟用本地結構評估"];
  }

  const forbiddenHits = result.forbidden_word_check?.total_hits || 0;
  const unresolvedForeshadow =
    result.story_memory_check?.stats?.unresolved_foreshadow_count || 0;
  const arcWarnings = result.arc_check?.warnings?.length || 0;
  const renderWarnings = result.render_input_check?.warnings?.length || 0;

  return [
    statusLine(
      result.rule_check?.passed,
      "規則完整",
      "規則引用仍需檢查",
    ),
    statusLine(
      forbiddenHits === 0,
      "未偵測到禁忌詞",
      `偵測到 ${forbiddenHits} 個禁忌詞`,
    ),
    unresolvedForeshadow > 0
      ? `⚠ 有 ${unresolvedForeshadow} 個伏筆尚未 payoff`
      : "✅ 伏筆狀態已收斂",
    arcWarnings > 0
      ? `⚠ Arc 結構有 ${arcWarnings} 個提醒`
      : "✅ Arc 結構完整",
    renderWarnings > 0
      ? `⚠ Render input 有 ${renderWarnings} 個提醒`
      : "✅ Render input 可用",
  ];
}

function updateOutputData(output, setOutput, patch) {
  const data = output?.data || {};
  setOutput({
    ...(output || {}),
    success: true,
    message: output?.message || "Updated.",
    data: {
      ...data,
      ...patch,
    },
  });
}

export default function EvalSummary({ output, loading, setOutput, setLoading }) {
  const data = output?.data || {};
  const storyboard = data.storyboard || null;
  const evalResult = data.eval_result || null;
  const result = finalEval(evalResult);
  const manualEval = data.manual_eval || null;
  const manualPrompt = data.manual_eval_prompt || "";
  const manualResponse = data.manual_eval_response || "";

  if (!storyboard && !result && !manualEval) {
    return null;
  }

  async function handleManualPrompt() {
    if (!storyboard || loading) {
      return;
    }

    setLoading(true);
    try {
      const response = await generateManualEvalPrompt({
        storyboard,
        eval_result: evalResult,
        forbidden_words_text: "",
      });
      updateOutputData(output, setOutput, response.data || {});
      setOutput((current) => ({
        ...current,
        success: response.success,
        message: response.message,
      }));
    } catch (error) {
      setOutput({
        ...(output || {}),
        success: false,
        message: "人工評估 Prompt 產生失敗",
        error: error.message,
        data,
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleManualImport() {
    if (!manualResponse.trim() || loading) {
      return;
    }

    setLoading(true);
    try {
      const response = await importManualEval({
        manual_eval_text: manualResponse,
      });
      updateOutputData(output, setOutput, {
        ...(response.data || {}),
        manual_eval_response: manualResponse,
      });
      setOutput((current) => ({
        ...current,
        success: response.success,
        message: response.message,
      }));
    } catch (error) {
      setOutput({
        ...(output || {}),
        success: false,
        message: "人工評估匯入失敗",
        error: error.message,
        data,
      });
    } finally {
      setLoading(false);
    }
  }

  function setManualResponse(value) {
    updateOutputData(output, setOutput, { manual_eval_response: value });
  }

  return (
    <section className="creator-card">
      <h3>評估結果</h3>
      <p className="muted">
        本地評估會真的檢查規則引用、禁忌詞、伏筆、Arc 與 Render input，
        全程不呼叫 API。故事品質可用下方人工評估流程補強。
      </p>

      <h4>本地結構評估</h4>
      <ul className="eval-list">
        {localEvalLines(result).map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>

      {manualEval && (
        <div className="manual-eval-result">
          <h4>人工進階評估</h4>
          <div className="score-row">
            <strong>{manualEval.overall_score}/5</strong>
            <span>{manualEval.passed ? "可進下一步" : "建議先修稿"}</span>
          </div>
          {manualEval.summary && <p>{manualEval.summary}</p>}
          {manualEval.issues?.length > 0 && (
            <>
              <b>主要問題</b>
              <ul>
                {manualEval.issues.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          )}
          {manualEval.suggestions?.length > 0 && (
            <>
              <b>修正建議</b>
              <ul>
                {manualEval.suggestions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      <details className="manual-eval-panel">
        <summary>免費人工評估：產生 Prompt / 貼回結果</summary>
        <div className="manual-eval-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={handleManualPrompt}
            disabled={!storyboard || loading}
          >
            產生評估 Prompt
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={() => navigator.clipboard?.writeText(manualPrompt)}
            disabled={!manualPrompt}
          >
            複製評估 Prompt
          </button>
        </div>
        <textarea
          className="mono"
          rows={8}
          readOnly
          value={manualPrompt}
          placeholder="按下「產生評估 Prompt」後，貼到 ChatGPT / Claude / Gemini。"
        />
        <textarea
          className="mono"
          rows={8}
          value={manualResponse}
          onChange={(event) => setManualResponse(event.target.value)}
          placeholder="把模型回傳的評估 JSON 貼在這裡。"
        />
        <button
          type="button"
          onClick={handleManualImport}
          disabled={!manualResponse.trim() || loading}
        >
          匯入人工評估
        </button>
      </details>
    </section>
  );
}
