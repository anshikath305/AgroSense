import { NextResponse } from "next/server";
import { BACKEND_URL, postJsonToBackend } from "@/lib/backend";

type AdvisoryRequest = {
  query: string;
  lang?: string;
  disease_result?: Record<string, unknown> | null;
};

function parseBackendError(body: string, status: number) {
  let message = body || `Backend request failed: ${status}`;
  try {
    const parsed = JSON.parse(body) as { detail?: string; error?: string };
    message = parsed.detail || parsed.error || message;
  } catch {
    message = body || message;
  }
  return message;
}

export async function POST(request: Request) {
  try {
    const contentType = request.headers.get("content-type") ?? "";
    if (contentType.includes("multipart/form-data")) {
      const response = await fetch(`${BACKEND_URL}/advisory/ask`, {
        method: "POST",
        body: await request.formData(),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(parseBackendError(errorBody, response.status));
      }

      return NextResponse.json(await response.json());
    }

    const body = (await request.json()) as AdvisoryRequest;
    const data = await postJsonToBackend("/advisory/ask", body);
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      {
        error: "Advisory model request failed",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}
