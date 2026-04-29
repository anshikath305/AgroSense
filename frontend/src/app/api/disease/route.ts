import { NextResponse } from "next/server";
import { BACKEND_URL } from "@/lib/backend";

export async function POST(request: Request) {
  const formData = await request.formData();

  try {
    const response = await fetch(`${BACKEND_URL}/disease/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const body = await response.text();
      let message = body || `Backend request failed: ${response.status}`;
      try {
        const parsed = JSON.parse(body) as { detail?: string; error?: string };
        message = parsed.detail || parsed.error || message;
      } catch {
        message = body || message;
      }
      throw new Error(message);
    }

    return NextResponse.json(await response.json());
  } catch (error) {
    return NextResponse.json(
      {
        error: "Disease model request failed",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}
