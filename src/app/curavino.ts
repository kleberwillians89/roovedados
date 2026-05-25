const envDefaultClientId = String(import.meta.env.VITE_DEFAULT_CLIENT_ID || "").trim();

let hasLoggedConfigWarning = false;

export const CURAVINO_CLIENT_ID = envDefaultClientId;
export const CURAVINO_CLIENT_NAME = "Curavino";

// Legacy export names kept so existing imports continue to work in this Curavino-only copy.
export const ROOVE_CLIENT_ID = CURAVINO_CLIENT_ID;
export const ROOVE_CLIENT_NAME = CURAVINO_CLIENT_NAME;
export const ROOVE_APP_NAME = "Curavino Metrics";
export const ROOVE_PANEL_NAME = "Painel Curavino";
export const IS_ROOVE_CLIENT_ID_FALLBACK = !envDefaultClientId;
export const ACTIVE_CLIENT_ID = CURAVINO_CLIENT_ID;
export const ACTIVE_CLIENT_NAME = CURAVINO_CLIENT_NAME;
export const DEFAULT_CLIENT_ID = envDefaultClientId;

export const GA4_CLIENT_OPTIONS = [
  { id: CURAVINO_CLIENT_ID, name: CURAVINO_CLIENT_NAME },
];

export function getCuravinoClientConfigurationWarning(): string | null {
  if (envDefaultClientId) return null;
  return "VITE_DEFAULT_CLIENT_ID nao foi definido.";
}

export function getCuravinoClientId(): string {
  const warning = getCuravinoClientConfigurationWarning();
  if (warning && !hasLoggedConfigWarning) {
    hasLoggedConfigWarning = true;
    console.warn(`[curavino-config] ${warning}`);
  }
  return ACTIVE_CLIENT_ID;
}
