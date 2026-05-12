import React, { useMemo, useState } from "react";

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
    title: "語音腳本",
    description: "產生每場景 TTS 腳本與預計檔名。",
    action: generateVoiceProject,
    dataKey: "voice_project",
    readyText: "語音稿已就緒",
    countLabel: "段語音",
  },
  {
    id: "images",
    label: "生成圖片",
    title: "圖片提示詞",
    description: "產生每場景 image prompt 與負面提示詞。",
    action: generateImagePromptProject,
    dataKey: "image_prompt_project",
    readyText: "圖片提示詞已就緒",
    countLabel: "張圖片",
  },
  {
    id: "storyboard",
    label: "生成分鏡",
    title: "分鏡表",
    description: "把 render scene 轉成一場一鏡的 shot list。",
    action: generateShotStoryboard,
    dataKey: "shot_storyboard",
    readyText: "分鏡表已就緒",
    countLabel: "個鏡頭",
  },
  {
    id: "video",
    label: "生成影片",
    title: "影片組裝清單",
    description: "產生未來 ffmpeg/render pipeline 可讀的素材組裝 manifest。",
    action: generateVideoManifest,
    dataKey: "video_manifest",
    readyText: "影片組裝清單已就緒",
    countLabel: "段影片",
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

function downloadJson(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function copyProjectText(key, project) {
  if (key === "voice_project") {
    return (project.lines || [])
      .map((line) => `${line.scene_id} ${line.title}\n${line.text}`)
      .join("\n\n");
  }
  if (key === "image_prompt_project") {
    return (project.items || [])
      .map((item) => `${item.scene_id} ${item.title}\n${item.prompt}`)
      .join("\n\n");
  }
  if (key === "shot_storyboard") {
    return (project.shots || [])
      .map(
        (shot) =>
          `${shot.shot_id} / ${shot.scene_id} / ${shot.duration_sec}s\n` +
          `${shot.camera_style} / ${shot.transition_type}\n${shot.subtitle_text}`,
      )
      .join("\n\n");
  }
  if (key === "video_manifest") {
    return (project.scenes || [])
      .map(
        (scene) =>
          `${scene.scene_id} ${scene.duration_sec}s\n` +
          `image=${scene.image_asset}\nvoice=${scene.voice_asset}`,
      )
      .join("\n\n");
  }
  return JSON.stringify(project, null, 2);
}

function previewItems(key, project) {
  if (key === "voice_project") {
    return (project.lines || []).slice(0, 3).map((line) => ({
      id: line.scene_id,
      title: line.title,
      meta: `${line.duration_sec}s / ${line.voice_style}`,
      body: line.text,
    }));
  }
  if (key === "image_prompt_project") {
    return (project.items || []).slice(0, 3).map((item) => ({
      id: item.scene_id,
      title: item.title,
      meta: `${item.visual_style} / ${item.aspect_ratio}`,
      body: item.prompt,
    }));
  }
  if (key === "shot_storyboard") {
    return (project.shots || []).slice(0, 3).map((shot) => ({
      id: shot.shot_id,
      title: `${shot.scene_id} ${shot.title}`,
      meta: `${shot.duration_sec}s / ${shot.camera_style} / ${shot.transition_type}`,
      body: shot.subtitle_text,
    }));
  }
  if (key === "video_manifest") {
    return (project.scenes || []).slice(0, 3).map((scene) => ({
      id: scene.scene_id,
      title: `${scene.duration_sec}s`,
      meta: `${scene.image_asset} + ${scene.voice_asset}`,
      body: scene.subtitle_text,
    }));
  }
  return [];
}

export default function NextStepPanel({
  output,
  setOutput,
  loading,
  setLoading,
}) {
  const [copiedKey, setCopiedKey] = useState("");
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
      setCopiedKey("");
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

  async function copyProject(step) {
    const project = data[step.dataKey];
    if (!project) {
      return;
    }
    const text = copyProjectText(step.dataKey, project);
    try {
      await navigator.clipboard?.writeText(text);
      setCopiedKey(step.dataKey);
    } catch {
      setCopiedKey("");
    }
  }

  return (
    <section className="creator-card">
      <div className="section-heading">
        <div>
          <h3>下一步工作流</h3>
          <p className="muted">
            v0.1 先產出本地製作包，不呼叫 TTS、圖片模型或 ffmpeg。
          </p>
        </div>
      </div>
      {!canRun && (
        <p className="status status-warn">
          請先完成 storyboard 生成或手動解析，才可以產生語音、圖片、分鏡與影片清單。
        </p>
      )}
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
              <span>{step.title}</span>
              <strong>
                {countForProject(step.dataKey, step.project)} {step.countLabel}
              </strong>
              <small>
                {step.project.status ||
                  step.project.format ||
                  step.project.notes?.[0] ||
                  "ready"}
              </small>
              <p>{step.description}</p>
              <div className="production-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => copyProject(step)}
                >
                  {copiedKey === step.dataKey ? "已複製" : "複製文字"}
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    downloadJson(`${step.id}_package.json`, step.project)
                  }
                >
                  下載 JSON
                </button>
              </div>
              <div className="production-preview">
                {previewItems(step.dataKey, step.project).map((item) => (
                  <div className="production-preview-item" key={item.id}>
                    <small>{item.id}</small>
                    <b>{item.title}</b>
                    <span>{item.meta}</span>
                    <p>{item.body}</p>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
