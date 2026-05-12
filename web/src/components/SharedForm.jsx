import React from "react";

const hiddenFieldIds = new Set(["forbidden_words"]);

function updateValue(current, id, value) {
  return {
    ...current,
    [id]: value,
  };
}

export default function SharedForm({ fields, value, onChange }) {
  function handleFieldChange(field, nextValue) {
    onChange(updateValue(value, field.id, nextValue));
  }

  return (
    <section className="panel">
      <h2>創作設定</h2>
      <div className="form-grid">
        {fields
          .filter((field) => !hiddenFieldIds.has(field.id))
          .map((field) => (
            <label key={field.id} className="field">
              <span>{field.label}</span>
              {field.type === "select" && (
                <select
                  value={value[field.id] ?? field.default ?? ""}
                  onChange={(event) => handleFieldChange(field, event.target.value)}
                >
                  {(field.options || []).map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              )}
              {field.type === "combobox" && (
                <>
                  <input
                    list={`${field.id}-options`}
                    value={value[field.id] ?? field.default ?? ""}
                    placeholder={field.placeholder || ""}
                    onChange={(event) =>
                      handleFieldChange(field, event.target.value)
                    }
                  />
                  <datalist id={`${field.id}-options`}>
                    {(field.options || []).map((option) => (
                      <option key={option} value={option} />
                    ))}
                  </datalist>
                </>
              )}
              {field.type === "number" && (
                <input
                  type="number"
                  value={value[field.id] ?? field.default ?? 0}
                  onChange={(event) =>
                    handleFieldChange(field, Number(event.target.value))
                  }
                />
              )}
              {field.type === "checkbox" && (
                <input
                  type="checkbox"
                  checked={Boolean(value[field.id] ?? field.default)}
                  onChange={(event) =>
                    handleFieldChange(field, event.target.checked)
                  }
                />
              )}
              {field.help_text && <small>{field.help_text}</small>}
            </label>
          ))}

        <label className="field span-all">
          <span>自訂禁忌詞</span>
          <textarea
            value={value.forbidden_words ?? ""}
            placeholder="每行一組：禁忌詞=替換詞"
            rows={4}
            onChange={(event) =>
              onChange(updateValue(value, "forbidden_words", event.target.value))
            }
          />
        </label>
      </div>
    </section>
  );
}
