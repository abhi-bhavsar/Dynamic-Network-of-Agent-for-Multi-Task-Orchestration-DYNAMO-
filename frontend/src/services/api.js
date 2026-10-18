import { generateSimulatedResponse, MOCK_AGENTS, MOCK_POLICIES } from './mockData';

let BASE_URL =
  (typeof window !== 'undefined' && localStorage.getItem('dynamo_api_url')) ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000';

export function setApiBaseUrl(url) {
  BASE_URL = url.replace(/\/+$/, '');
  try {
    if (typeof window !== 'undefined') {
      localStorage.setItem('dynamo_api_url', BASE_URL);
    }
  } catch (e) {
    // ignore local storage errors
  }
}

export function getApiBaseUrl() {
  return BASE_URL;
}


export async function checkHealth() {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(id);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      online: true,
      model: data.model || 'Groq',
      groqConnected: data.groq_connected,
      status: data.status,
      version: data.version || '1.0.0',
    };
  } catch (err) {
    return {
      online: false,
      model: 'Offline / Simulation Mode',
      groqConnected: false,
      status: 'offline',
      version: '1.0.0',
    };
  }
}

export async function fetchAgentFleet() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/agents`);
    if (res.ok) {
      const data = await res.json();
      return data.agents || MOCK_AGENTS;
    }
  } catch (err) {
    // fallback
  }
  return MOCK_AGENTS;
}

export async function fetchPolicies() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/policies`);
    if (res.ok) {
      const data = await res.json();
      return data.policies || MOCK_POLICIES;
    }
  } catch (err) {
    // fallback
  }
  return MOCK_POLICIES;
}

export async function executeQuery(query, sessionHistory = [], forceDemo = false) {
  if (forceDemo) {
    await new Promise((r) => setTimeout(r, 650));
    return generateSimulatedResponse(query, false);
  }

  try {
    const res = await fetch(`${BASE_URL}/api/v1/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_history: sessionHistory }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error: ${res.status}`);
    }

    const data = await res.json();
    return data;
  } catch (err) {
    console.warn('Backend unavailable, falling back to simulated execution:', err);
    await new Promise((r) => setTimeout(r, 650));
    const fallback = generateSimulatedResponse(query, false);
    fallback.isSimulated = true;
    fallback.simulatedReason = err.message;
    return fallback;
  }
}

export async function executeBenchmark(query, forceDemo = false) {
  if (forceDemo) {
    await new Promise((r) => setTimeout(r, 900));
    return generateSimulatedResponse(query, true);
  }

  try {
    const res = await fetch(`${BASE_URL}/api/v1/benchmark`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, runs: 1, include_static: true }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error: ${res.status}`);
    }

    const data = await res.json();
    return data;
  } catch (err) {
    console.warn('Backend unavailable, falling back to simulated benchmark:', err);
    await new Promise((r) => setTimeout(r, 900));
    const fallback = generateSimulatedResponse(query, true);
    fallback.isSimulated = true;
    fallback.simulatedReason = err.message;
    return fallback;
  }
}

export async function analyzePse(query) {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/pse/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (res.ok) return await res.json();
  } catch (err) {
    // fallback
  }

  // Client-side quick PSE simulation
  const lower = query.toLowerCase();
  let c = 2;
  if (lower.includes('comprehensive') || lower.includes('portfolio') || lower.includes('macro')) c = 5;
  else if (lower.includes('earnings') || lower.includes('analyze')) c = 3;

  return {
    query,
    feature_vector: { N: 0.75, U: 0.35, C: c, R: 0.1 },
    selected_policy: c >= 4 ? 'hierarchical' : 'on_demand',
    selected_agents: ['deploy_market', 'deploy_sentiment', 'deploy_fundamental'].slice(0, c),
    explanation: `Simulated policy calculation for query complexity ${c}/5.`,
  };
}
