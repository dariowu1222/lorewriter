import React, { useEffect, useMemo, useState } from "react";

import { getGenerationModes, getUIContract } from "./api.js";
import ManualPanel from "./components/ManualPanel.jsx";
import ModeTabs from "./components/ModeTabs.jsx";
import OpenAIPanel from "./components/OpenAIPanel.jsx";
import OutputPanel from "./components/OutputPanel.jsx";
import RuleEditor from "./components/RuleEditor.jsx";
import SharedForm from "./components/SharedForm.jsx";

const WORKSPACE_CACHE_KEY = "ai_writer_room.creator_workspace.v1";

const defaultSharedState = {
  sub_genre: "地鐵末班車",
  world_setting: "現代都市",
  horror_style: "規則恐怖",
  pacing_style: "高壓",
  ending_style: "尾刀",
  protagonist_type: "夜班人員",
  object_focus: "末班車票",
  visual_style: "cinematic",
  duration: 180,
  enable_eval: true,
  enable_auto_fix: false,
  export_render_input: true,
  forbidden_words: "",
  rule_count: 5,
  generated_rules: [],
  manual_prompt_text: "",
  manual_response_text: "",
};

function loadWorkspaceCache() {
  try {
    const cached = localStorage.getItem(WORKSPACE_CACHE_KEY);
    if (!cached) {
      return {};
    }
    return JSON.parse(cached);
  } catch {
    return {};
  }
}

function writeWorkspaceCache(snapshot) {
  try {
    localStorage.setItem(WORKSPACE_CACHE_KEY, JSON.stringify(snapshot));
  } catch {
    // Ignore storage quota or private-mode failures; generation can continue.
  }
}

export default function App() {
  const cachedWorkspace = useMemo(loadWorkspaceCache, []);
  const [contract, setContract] = useState(null);
  const [generationModes, setGenerationModes] = useState([]);
  const [activeMode, setActiveMode] = useState(
    cachedWorkspace.activeMode || "manual",
  );
  const [sharedState, setSharedState] = useState({
    ...defaultSharedState,
    ...(cachedWorkspace.sharedState || {}),
  });
  const [output, setOutput] = useState(cachedWorkspace.output || null);
  const [loading, setLoading] = useState(false);
  const [bootError, setBootError] = useState("");

  useEffect(() => {
    async function boot() {
      try {
        const [contractResponse, modesResponse] = await Promise.all([
          getUIContract(),
          getGenerationModes(),
        ]);
        setContract(contractResponse.data);
        setGenerationModes(modesResponse.data?.modes || []);
      } catch (error) {
        setBootError(error.message);
      }
    }

    boot();
  }, []);

  const activeModeInfo = useMemo(
    () => generationModes.find((mode) => mode.mode === activeMode),
    [activeMode, generationModes],
  );

  useEffect(() => {
    writeWorkspaceCache({
      activeMode,
      sharedState,
      output,
    });
  }, [activeMode, sharedState, output]);

  function saveWorkspaceCache(snapshotPatch = {}) {
    const nextSharedState = {
      ...sharedState,
      ...(snapshotPatch.sharedState || {}),
    };
    const nextOutput =
      Object.prototype.hasOwnProperty.call(snapshotPatch, "output")
        ? snapshotPatch.output
        : output;

    writeWorkspaceCache({
      activeMode,
      sharedState: nextSharedState,
      output: nextOutput,
    });
  }

  function updateSharedState(nextPartial) {
    setSharedState((current) => ({
      ...current,
      ...nextPartial,
    }));
  }

  if (bootError) {
    return (
      <main className="app-shell">
        <div className="status status-error">{bootError}</div>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">AI Writer Room v0.1</p>
          <h1>AI Horror Production Workspace</h1>
        </div>
        <div className="mode-summary">
          {activeModeInfo?.display_name || activeMode}
        </div>
      </header>

      <ModeTabs
        tabs={contract?.tabs || []}
        activeMode={activeMode}
        onChange={setActiveMode}
      />

      <section className="workspace">
        <div className="control-column">
          <RuleEditor
            value={sharedState}
            onChange={updateSharedState}
            loading={loading}
            setLoading={setLoading}
            setOutput={setOutput}
            onSave={saveWorkspaceCache}
          />

          <SharedForm
            fields={contract?.shared_fields || []}
            value={sharedState}
            onChange={setSharedState}
          />

          {activeMode === "manual" ? (
            <ManualPanel
              sharedState={sharedState}
              onSharedStateChange={updateSharedState}
              loading={loading}
              setLoading={setLoading}
              setOutput={setOutput}
            />
          ) : (
            <OpenAIPanel
              sharedState={sharedState}
              fields={contract?.openai_fields || []}
              loading={loading}
              setLoading={setLoading}
              setOutput={setOutput}
            />
          )}
        </div>

        <OutputPanel output={output} loading={loading} />
      </section>
    </main>
  );
}
