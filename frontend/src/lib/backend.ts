export const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.AGROSENSE_BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "http://127.0.0.1:8001";

export async function postJsonToBackend<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Backend request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
