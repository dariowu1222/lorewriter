const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || payload.message || "API request failed.");
  }
  return payload;
}

export function getUIContract() {
  return request("/api/ui-contract");
}

export function getGenerationModes() {
  return request("/api/generation-modes");
}

export function generateRules(payload) {
  return request("/api/rules/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateManualPrompt(payload) {
  return request("/api/manual/generate-prompt", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function parseManualResponse(payload) {
  return request("/api/manual/parse-response", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateWithOpenAI(payload) {
  return request("/api/openai/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateVoiceProject(payload) {
  return request("/api/production/voice", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateImagePromptProject(payload) {
  return request("/api/production/images", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateShotStoryboard(payload) {
  return request("/api/production/storyboard", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateVideoManifest(payload) {
  return request("/api/production/video", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
