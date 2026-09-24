import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const backendUrl = 'http://127.0.0.1:8000/api/doc_count';
    const response = await fetch(backendUrl);
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { count: 0, detail: `Proxy error: ${error.message}` },
      { status: 500 }
    );
  }
}
