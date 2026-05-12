import React from "react";

export default function RuleListCard({ rules }) {
  if (!rules?.length) {
    return null;
  }

  return (
    <section className="creator-card">
      <h3>規則列表</h3>
      <div className="rule-card-list">
        {rules.map((rule) => (
          <article className="rule-card" key={rule.id}>
            <span>{rule.id}</span>
            <strong>{rule.text}</strong>
            <em>{rule.category || "未分類"}</em>
          </article>
        ))}
      </div>
    </section>
  );
}
