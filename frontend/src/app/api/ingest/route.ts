import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const backendUrl = 'http://127.0.0.1:8000/api/ingest';

    const response = await fetch(backendUrl, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { detail: data.detail || data.message || 'Backend ingestion failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Next.js Proxy Error: ${error.message || String(error)}` },
      { status: 500 }
    );
  }
}
