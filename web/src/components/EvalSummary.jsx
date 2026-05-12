import React from "react";

function finalEval(evalResult) {
  if (!evalResult) {
    return null;
  }
  return evalResult.after_fix || evalResult;
}

function statusLine(ok, successText, warningText) {
  return ok ? `✅ ${successText}` : `⚠ ${warningText}`;
}

export default function EvalSummary({ evalResult }) {
  const result = finalEval(evalResult);
  if (!result) {
    return null;
  }

  const forbiddenHits = result.forbidden_word_check?.total_hits || 0;
  const unresolvedForeshadow =
    result.story_memory_check?.stats?.unresolved_foreshadow_count || 0;
  const arcWarnings = result.arc_check?.warnings?.length || 0;
  const renderWarnings = result.render_input_check?.warnings?.length || 0;

  const lines = [
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

  return (
    <section className="creator-card">
      <h3>評估結果</h3>
      <ul className="eval-list">
        {lines.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </section>
  );
}
