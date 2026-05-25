const envClientId = String(import.meta.env.VITE_DEFAULT_CLIENT_ID || "").trim();
const envApiBase = String(import.meta.env.VITE_API_BASE || "").trim();

let hasLoggedConfigWarning = false;

export const ROOVE_CLIENT_NAME = "Roove";
export const ROOVE_APP_NAME = "Roove Metrics";
export const ROOVE_PANEL_NAME = "Painel Roove";
export const ROOVE_CLIENT_ID = envClientId;
export const DEFAULT_CLIENT_ID = envClientId;
export const API_BASE = envApiBase;
export const IS_DEFAULT_CLIENT_ID_MISSING = !envClientId;

export function getRooveClientConfigurationWarning(): string | null {
  if (!IS_DEFAULT_CLIENT_ID_MISSING) return null;
  return [
    "VITE_DEFAULT_CLIENT_ID nao foi definido.",
    "Configure o client_id correto para liberar integracoes e dados em producao.",
  ].join(" ");
}

export function getDefaultClientId(): string {
  const warning = getRooveClientConfigurationWarning();
  if (warning && !hasLoggedConfigWarning) {
    hasLoggedConfigWarning = true;
    console.warn(`[client-config] ${warning}`);
  }
  return DEFAULT_CLIENT_ID;
}

export function getRooveClientId(): string {
  return getDefaultClientId();
}
