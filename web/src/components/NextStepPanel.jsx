import React from "react";

const steps = ["生成語音", "生成圖片", "生成分鏡", "生成影片"];

export default function NextStepPanel() {
  return (
    <section className="creator-card">
      <h3>下一步工作流</h3>
      <div className="next-step-row">
        {steps.map((step) => (
          <button key={step} type="button" disabled title="planned in v0.2">
            {step}
          </button>
        ))}
      </div>
    </section>
  );
}
