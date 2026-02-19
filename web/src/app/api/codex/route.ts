/**
 * Server-side proxy for Codex.io GraphQL API.
 *
 * Reads CODEX_API_KEY from Vercel environment variables so the key
 * is never exposed to the client. Set the key in Vercel Dashboard:
 *   Settings > Environment Variables > CODEX_API_KEY
 */

import { NextRequest, NextResponse } from "next/server";

const CODEX_ENDPOINT = "https://graph.codex.io/graphql";

export async function POST(request: NextRequest) {
  const apiKey = process.env.CODEX_API_KEY;

  if (!apiKey) {
    return NextResponse.json(
      { error: "CODEX_API_KEY is not configured. Add it in Vercel Dashboard > Settings > Environment Variables." },
      { status: 500 },
    );
  }

  try {
    const body = await request.json();

    const response = await fetch(CODEX_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: apiKey,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const text = await response.text();
      return NextResponse.json(
        { error: `Codex API returned ${response.status}`, details: text },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}

/** Health check — confirms the key is set (without revealing it). */
export async function GET() {
  const configured = !!process.env.CODEX_API_KEY;
  return NextResponse.json({
    status: configured ? "ready" : "missing_key",
    message: configured
      ? "Codex API key is configured. POST a GraphQL query to this endpoint."
      : "CODEX_API_KEY not set. Add it in Vercel Dashboard > Settings > Environment Variables.",
  });
}
