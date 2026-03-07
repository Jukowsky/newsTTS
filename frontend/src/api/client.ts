const BASE = "/api";

export interface Portal {
  id: string;
  name: string;
  language: string;
}

export interface Article {
  id: number;
  title: string;
  author: string;
  date: string;
  url: string;
  word_count: number;
  scraped_at: string;
  audio_url: string | null;
}

export interface PortalTTSSettings {
  tts_engine: string;
  elevenlabs_api_key: string;
  elevenlabs_voice_id: string;
  gemini_api_key: string;
  gemini_voice_name: string;
}

export type AdminSettings = Record<string, PortalTTSSettings>;

function adminHeaders(password: string): Record<string, string> {
  return {
    "Content-Type": "application/json",
    "x-admin-password": password,
  };
}

export async function fetchPortals(): Promise<Portal[]> {
  const res = await fetch(`${BASE}/portals`);
  if (!res.ok) throw new Error("Failed to fetch portals");
  return res.json();
}

export async function fetchArticles(portalId: string): Promise<Article[]> {
  const res = await fetch(`${BASE}/portals/${portalId}/articles`);
  if (!res.ok) throw new Error("Failed to fetch articles");
  return res.json();
}

export async function adminLogin(password: string): Promise<boolean> {
  const res = await fetch(`${BASE}/admin/login`, {
    method: "POST",
    headers: adminHeaders(password),
  });
  return res.ok;
}

export async function triggerScrape(
  portalId: string,
  password: string,
): Promise<{ portal: string; articles_processed: number; error: string | null }> {
  const res = await fetch(`${BASE}/admin/scrape/${portalId}`, {
    method: "POST",
    headers: adminHeaders(password),
  });
  if (!res.ok) throw new Error("Scrape failed");
  return res.json();
}

export async function fetchAdminSettings(
  password: string
): Promise<AdminSettings> {
  const res = await fetch(`${BASE}/admin/settings`, {
    headers: adminHeaders(password),
  });
  if (!res.ok) throw new Error("Failed to fetch settings");
  return res.json();
}

export async function updatePortalSettings(
  portalId: string,
  password: string,
  body: Partial<PortalTTSSettings>
): Promise<AdminSettings> {
  const res = await fetch(`${BASE}/admin/settings/${portalId}`, {
    method: "PUT",
    headers: adminHeaders(password),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Failed to update settings");
  return res.json();
}
