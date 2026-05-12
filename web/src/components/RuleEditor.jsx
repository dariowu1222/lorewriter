import React, { useState } from "react";

import { generateRules } from "../api.js";

function normalizeRule(rule, index) {
  return {
    id: rule.id || `R${String(index + 1).padStart(2, "0")}`,
    text: rule.text || "",
    category: rule.category || "自訂規則",
  };
}

export default function RuleEditor({
  value,
  onChange,
  loading,
  setLoading,
  setOutput,
  onSave,
}) {
  const rules = value.generated_rules || [];
  const [saveMessage, setSaveMessage] = useState("");

  async function handleGenerateRules() {
    setLoading(true);
    try {
      const response = await generateRules({
        sub_genre: value.sub_genre,
        horror_style: value.horror_style,
        pacing_style: value.pacing_style,
        ending_style: value.ending_style,
        rule_count: value.rule_count,
      });
      onChange({ generated_rules: response.data.rules });
      setOutput(response);
    } catch (error) {
      setOutput({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  }

  function updateRule(index, patch) {
    const nextRules = rules.map((rule, ruleIndex) =>
      ruleIndex === index ? { ...rule, ...patch } : rule,
    );
    onChange({ generated_rules: nextRules });
  }

  function addRule() {
    const nextIndex = rules.length + 1;
    onChange({
      generated_rules: [
        ...rules,
        {
          id: `R${String(nextIndex).padStart(2, "0")}`,
          text: "",
          category: "自訂規則",
        },
      ],
    });
  }

  function deleteRule(index) {
    onChange({
      generated_rules: rules.filter((_, ruleIndex) => ruleIndex !== index),
    });
  }

  function saveRules() {
    const savedRules = rules.map((rule, index) => normalizeRule(rule, index));
    const savedOutput = {
      success: true,
      message: "Rules saved.",
      data: {
        rules: savedRules,
      },
    };

    onChange({ generated_rules: savedRules });
    setOutput(savedOutput);
    onSave?.({
      sharedState: {
        generated_rules: savedRules,
      },
      output: savedOutput,
    });
    setSaveMessage("規則已儲存到本機快取");
    window.setTimeout(() => setSaveMessage(""), 2000);
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Rule-first workflow</p>
          <h2>規則設定</h2>
        </div>
        <button type="button" onClick={handleGenerateRules} disabled={loading}>
          生成規則
        </button>
      </div>

      <label className="field compact-field">
        <span>規則數量</span>
        <input
          type="number"
          min="3"
          max="10"
          value={value.rule_count}
          onChange={(event) =>
            onChange({
              rule_count: Math.min(
                Math.max(Number(event.target.value) || 3, 3),
                10,
              ),
            })
          }
        />
      </label>

      <div className="rule-list">
        {rules.map((rule, index) => {
          const normalized = normalizeRule(rule, index);
          return (
            <div className="rule-row" key={`${normalized.id}-${index}`}>
              <div className="rule-id">{normalized.id}</div>
              <input
                value={normalized.text}
                onChange={(event) =>
                  updateRule(index, { text: event.target.value })
                }
                placeholder="輸入規則內容"
              />
              <input
                value={normalized.category}
                onChange={(event) =>
                  updateRule(index, { category: event.target.value })
                }
                placeholder="分類"
              />
              <button type="button" onClick={() => deleteRule(index)}>
                刪除
              </button>
            </div>
          );
        })}
      </div>

      <button type="button" className="secondary-button" onClick={addRule}>
        新增規則
      </button>
      <button type="button" onClick={saveRules}>
        儲存規則
      </button>
      {saveMessage && <div className="status status-ok">{saveMessage}</div>}
    </section>
  );
}
