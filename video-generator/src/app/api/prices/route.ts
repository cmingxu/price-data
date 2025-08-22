import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    
    // 构建后端API URL
    const apiURL = process.env.API_URL || "http://localhost:8001"
    const backendUrl = `${apiURL}/api/prices${queryString ? `?${queryString}` : ''}`;
    
    // 代理请求到后端API
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // 返回数据，Next.js会自动处理CORS
    return NextResponse.json(data);
  } catch (error) {
    console.error('Proxy API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from backend' },
      { status: 500 }
    );
  }
}