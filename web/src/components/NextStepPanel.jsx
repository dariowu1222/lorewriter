import React, { useMemo } from "react";

import {
  generateImagePromptProject,
  generateShotStoryboard,
  generateVideoManifest,
  generateVoiceProject,
} from "../api.js";

const steps = [
  {
    id: "voice",
    label: "生成語音",
    action: generateVoiceProject,
    dataKey: "voice_project",
    readyText: "語音稿已就緒",
  },
  {
    id: "images",
    label: "生成圖片",
    action: generateImagePromptProject,
    dataKey: "image_prompt_project",
    readyText: "圖片提示詞已就緒",
  },
  {
    id: "storyboard",
    label: "生成分鏡",
    action: generateShotStoryboard,
    dataKey: "shot_storyboard",
    readyText: "分鏡表已就緒",
  },
  {
    id: "video",
    label: "生成影片",
    action: generateVideoManifest,
    dataKey: "video_manifest",
    readyText: "影片組裝清單已就緒",
  },
];

function countForProject(key, project) {
  if (!project) {
    return 0;
  }
  if (key === "voice_project") {
    return project.lines?.length || 0;
  }
  if (key === "image_prompt_project") {
    return project.items?.length || 0;
  }
  if (key === "shot_storyboard") {
    return project.shots?.length || 0;
  }
  if (key === "video_manifest") {
    return project.scenes?.length || 0;
  }
  return 0;
}

export default function NextStepPanel({
  output,
  setOutput,
  loading,
  setLoading,
}) {
  const data = output?.data || {};
  const storyboard = data.storyboard || null;
  const renderProject = data.render_project || null;
  const canRun = Boolean(storyboard || renderProject);
  const visualStyle = storyboard?.story_bible?.visual_style || null;

  const productionCards = useMemo(
    () =>
      steps
        .map((step) => ({
          ...step,
          project: data[step.dataKey],
        }))
        .filter((step) => step.project),
    [data],
  );

  async function runStep(step) {
    if (!canRun || loading) {
      return;
    }

    setLoading(true);
    try {
      const response = await step.action({
        storyboard,
        render_project: renderProject,
        visual_style: visualStyle,
      });
      setOutput({
        success: response.success,
        message: response.message,
        data: {
          ...data,
          ...(response.data || {}),
        },
      });
    } catch (error) {
      setOutput({
        success: false,
        message: `${step.label}失敗`,
        error: error.message,
        data,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="creator-card">
      <div className="section-heading">
        <div>
          <h3>下一步工作流</h3>
          <p className="muted">
            v0.1 先產出本地素材包，不呼叫 TTS、圖片模型或 ffmpeg。
          </p>
        </div>
      </div>
      <div className="next-step-row">
        {steps.map((step) => (
          <button
            key={step.id}
            type="button"
            disabled={!canRun || loading}
            title={canRun ? step.readyText : "請先完成 storyboard 或 render input"}
            onClick={() => runStep(step)}
          >
            {step.label}
          </button>
        ))}
      </div>

      {productionCards.length > 0 && (
        <div className="production-grid">
          {productionCards.map((step) => (
            <article className="production-card" key={step.id}>
              <span>{step.readyText}</span>
              <strong>{countForProject(step.dataKey, step.project)} 項</strong>
              <small>
                {step.project.status ||
                  step.project.format ||
                  step.project.notes?.[0] ||
                  "ready"}
              </small>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
