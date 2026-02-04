import { NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { getWorkflowRuns } from "@/lib/github"

export async function GET(request: NextRequest) {
  const session = await getSession()
  
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
  
  const searchParams = request.nextUrl.searchParams
  const workflowId = searchParams.get("workflowId")
  const limit = parseInt(searchParams.get("limit") || "10", 10)
  
  try {
    const runs = await getWorkflowRuns(
      session.accessToken, 
      workflowId ? parseInt(workflowId, 10) : undefined,
      limit
    )
    
    return NextResponse.json({ runs })
  } catch (error) {
    console.error("Failed to get workflow runs:", error)
    return NextResponse.json(
      { error: "Failed to get workflow runs" }, 
      { status: 500 }
    )
  }
}
