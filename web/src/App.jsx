import { useEffect, useMemo, useState } from "react";

import { getGenerationModes, getUIContract } from "./api.js";
import ManualPanel from "./components/ManualPanel.jsx";
import ModeTabs from "./components/ModeTabs.jsx";
import OpenAIPanel from "./components/OpenAIPanel.jsx";
import OutputPanel from "./components/OutputPanel.jsx";
import SharedForm from "./components/SharedForm.jsx";

const defaultSharedState = {
  sub_genre: "地鐵末班車",
  duration: 180,
  enable_eval: true,
  enable_auto_fix: false,
  export_render_input: true,
  forbidden_words: "",
};

export default function App() {
  const [contract, setContract] = useState(null);
  const [generationModes, setGenerationModes] = useState([]);
  const [activeMode, setActiveMode] = useState("manual");
  const [sharedState, setSharedState] = useState(defaultSharedState);
  const [output, setOutput] = useState(null);
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
          <h1>規則怪談生成室</h1>
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
          <SharedForm
            fields={contract?.shared_fields || []}
            value={sharedState}
            onChange={setSharedState}
          />

          {activeMode === "manual" ? (
            <ManualPanel
              sharedState={sharedState}
              fields={contract?.manual_fields || []}
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
