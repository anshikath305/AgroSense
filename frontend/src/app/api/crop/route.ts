import { NextResponse } from "next/server";
import { postJsonToBackend } from "@/lib/backend";

type CropRequest = {
  N: number;
  P: number;
  K: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
};

export async function POST(request: Request) {
  const body = (await request.json()) as CropRequest;

  try {
    const data = await postJsonToBackend("/crop/predict", body);
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      {
        error: "Crop model request failed",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}
