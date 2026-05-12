import React from "react";

export default function ArcTimeline({ arcPlan }) {
  const arcs = arcPlan?.arcs || [];
  if (!arcs.length) {
    return null;
  }

  return (
    <section className="creator-card">
      <h3>故事結構</h3>
      <div className="arc-grid">
        {arcs.map((arc) => (
          <article className="arc-card" key={arc.id}>
            <div className="arc-card-header">
              <span>{arc.id}</span>
              <strong>{arc.name}</strong>
            </div>
            <p>{arc.purpose}</p>
            <p className="muted">{arc.emotional_goal}</p>
            <span className="tag">{arc.twist_type || "無反轉標記"}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
