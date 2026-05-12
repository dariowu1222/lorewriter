import React from "react";

function countArcs(storyboard) {
  return storyboard?.arc_plan?.arcs?.length || 0;
}

function summaryText(storyboard) {
  const title = storyboard?.title || "尚未生成";
  const firstRule = storyboard?.story_bible?.world_rules?.[0]?.text;
  return firstRule ? `${title}：${firstRule}` : `${title} 的規則怪談草稿。`;
}

export default function StorySummaryCard({ storyboard }) {
  if (!storyboard) {
    return null;
  }

  return (
    <section className="creator-card">
      <h3>故事摘要</h3>
      <dl className="summary-grid">
        <div>
          <dt>標題</dt>
          <dd>{storyboard.title}</dd>
        </div>
        <div>
          <dt>子類型</dt>
          <dd>{storyboard.sub_genre}</dd>
        </div>
        <div>
          <dt>時長</dt>
          <dd>{storyboard.target_duration_sec} 秒</dd>
        </div>
        <div>
          <dt>場景</dt>
          <dd>{storyboard.scenes?.length || 0}</dd>
        </div>
        <div>
          <dt>Arc</dt>
          <dd>{countArcs(storyboard)}</dd>
        </div>
      </dl>
      <p className="story-summary">{summaryText(storyboard)}</p>
    </section>
  );
}
