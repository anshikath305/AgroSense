import { NextResponse } from "next/server";
import { postJsonToBackend } from "@/lib/backend";

type FertilizerRequest = {
  temperature: number;
  humidity: number;
  moisture: number;
  soil_type: string;
  crop_type: string;
  nitrogen: number;
  potassium: number;
  phosphorous: number;
};

export async function POST(request: Request) {
  const body = (await request.json()) as FertilizerRequest;

  try {
    const data = await postJsonToBackend("/fertilizer/predict", body);
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      {
        error: "Fertilizer model request failed",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}
