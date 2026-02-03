import { NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { triggerWorkflow, listWorkflows } from "@/lib/github"

export async function POST(request: NextRequest) {
  const session = await getSession()
  
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
  
  try {
    const body = await request.json()
    const { workflowId, ref = "master", inputs = {} } = body
    
    if (!workflowId) {
      return NextResponse.json({ error: "workflowId is required" }, { status: 400 })
    }
    
    await triggerWorkflow(session.accessToken, workflowId, ref, inputs)
    
    return NextResponse.json({ 
      success: true, 
      message: `Workflow ${workflowId} triggered successfully` 
    })
    
  } catch (error) {
    console.error("Failed to trigger workflow:", error)
    return NextResponse.json(
      { error: "Failed to trigger workflow" }, 
      { status: 500 }
    )
  }
}

export async function GET() {
  const session = await getSession()
  
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
  
  try {
    const workflows = await listWorkflows(session.accessToken)
    return NextResponse.json({ workflows })
  } catch (error) {
    console.error("Failed to list workflows:", error)
    return NextResponse.json(
      { error: "Failed to list workflows" }, 
      { status: 500 }
    )
  }
}
