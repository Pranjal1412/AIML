import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const policyMode = searchParams.get('policy_mode') || 'fixed_rule';
    const backendUrl = `http://127.0.0.1:8000/api/evaluate?policy_mode=${policyMode}`;

    const response = await fetch(backendUrl, { method: 'POST' });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Proxy error: ${error.message}` },
      { status: 500 }
    );
  }
}
