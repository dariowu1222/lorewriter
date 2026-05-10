import React from "react";

export default function ModeTabs({ tabs, activeMode, onChange }) {
  return (
    <nav className="mode-tabs" aria-label="Generation modes">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={tab.mode === activeMode ? "active" : ""}
          disabled={!tab.enabled}
          onClick={() => onChange(tab.mode)}
          title={tab.description}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
