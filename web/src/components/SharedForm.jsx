import React from "react";

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
      <h2>共用設定</h2>
      <div className="form-grid">
        {fields.map((field) => (
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
            {field.type === "textarea" && (
              <textarea
                value={value[field.id] ?? ""}
                placeholder={field.placeholder || ""}
                rows={5}
                onChange={(event) => handleFieldChange(field, event.target.value)}
              />
            )}
            {field.help_text && <small>{field.help_text}</small>}
          </label>
        ))}
      </div>
    </section>
  );
}
