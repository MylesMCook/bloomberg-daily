import { NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { getFileContent, updateFile } from "@/lib/github"
import YAML from "yaml"

const CONFIG_PATH = "config/sources.yaml"

export async function GET() {
  const session = await getSession()
  
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
  
  try {
    const { content, sha } = await getFileContent(session.accessToken, CONFIG_PATH)
    const config = YAML.parse(content)
    
    return NextResponse.json({ config, sha })
  } catch (error) {
    console.error("Failed to get sources config:", error)
    return NextResponse.json(
      { error: "Failed to get sources configuration" }, 
      { status: 500 }
    )
  }
}

export async function PUT(request: NextRequest) {
  const session = await getSession()
  
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
  
  try {
    const body = await request.json()
    const { config, sha, message = "Update sources configuration" } = body
    
    if (!config) {
      return NextResponse.json({ error: "config is required" }, { status: 400 })
    }
    
    // Validate config structure
    if (!config.version || !config.sources) {
      return NextResponse.json(
        { error: "Invalid config structure" }, 
        { status: 400 }
      )
    }
    
    // Convert to YAML
    const yamlContent = YAML.stringify(config, { 
      indent: 2,
      lineWidth: 0 // Disable line wrapping
    })
    
    await updateFile(
      session.accessToken,
      CONFIG_PATH,
      yamlContent,
      message,
      sha
    )
    
    return NextResponse.json({ 
      success: true, 
      message: "Configuration updated successfully" 
    })
    
  } catch (error) {
    console.error("Failed to update sources config:", error)
    return NextResponse.json(
      { error: "Failed to update sources configuration" }, 
      { status: 500 }
    )
  }
}
