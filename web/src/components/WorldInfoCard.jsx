import React from "react";

export default function WorldInfoCard({ storyBible }) {
  if (!storyBible) {
    return null;
  }

  return (
    <section className="creator-card">
      <h3>世界觀</h3>
      <p>{storyBible.world_summary || "尚未建立世界摘要。"}</p>
      <dl className="summary-grid">
        <div>
          <dt>核心主題</dt>
          <dd>{storyBible.core_theme || "未設定"}</dd>
        </div>
        <div>
          <dt>世界設定</dt>
          <dd>{storyBible.world_setting || "未設定"}</dd>
        </div>
        <div>
          <dt>恐怖類型</dt>
          <dd>{storyBible.horror_style || "未設定"}</dd>
        </div>
        <div>
          <dt>視覺風格</dt>
          <dd>{storyBible.visual_style || "未設定"}</dd>
        </div>
        <div>
          <dt>核心物件</dt>
          <dd>{storyBible.object_focus || "未設定"}</dd>
        </div>
      </dl>
      <div className="tag-row">
        {(storyBible.tone_keywords || []).map((keyword) => (
          <span key={keyword} className="tag">
            {keyword}
          </span>
        ))}
      </div>
    </section>
  );
}
