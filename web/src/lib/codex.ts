/**
 * Client-side helper for calling the Codex.io API through our server proxy.
 *
 * All requests go through /api/codex so the API key stays server-side.
 */

export interface GraphQLResponse<T = Record<string, unknown>> {
  data?: T;
  errors?: Array<{ message: string }>;
}

/**
 * Execute a Codex GraphQL query via the server-side proxy.
 * The API key is read from process.env.CODEX_API_KEY on the server.
 */
export async function codexQuery<T = Record<string, unknown>>(
  query: string,
  variables?: Record<string, unknown>,
): Promise<GraphQLResponse<T>> {
  const res = await fetch("/api/codex", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API request failed: ${res.status}`);
  }

  return res.json();
}

/**
 * Check if the Codex API key is configured on the server.
 */
export async function checkCodexStatus(): Promise<{
  status: "ready" | "missing_key";
  message: string;
}> {
  const res = await fetch("/api/codex");
  return res.json();
}
