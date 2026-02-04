/**
 * GitHub API Integration
 * 
 * Provides functions to interact with GitHub API for:
 * - Workflow management (trigger, status)
 * - Repository operations
 * - File management (read/write config)
 */

const REPO_OWNER = process.env.GITHUB_REPO_OWNER || "MylesMCook"
const REPO_NAME = process.env.GITHUB_REPO_NAME || "bloomberg-daily"

export interface WorkflowRun {
  id: number
  name: string
  status: "queued" | "in_progress" | "completed"
  conclusion: "success" | "failure" | "cancelled" | "skipped" | null
  created_at: string
  updated_at: string
  html_url: string
  head_sha: string
  head_branch: string
}

export interface Workflow {
  id: number
  name: string
  path: string
  state: "active" | "disabled"
}

export interface RepoFile {
  name: string
  path: string
  sha: string
  size: number
  type: "file" | "dir"
  download_url: string | null
}

/**
 * Make an authenticated GitHub API request
 */
async function githubFetch(
  endpoint: string,
  accessToken: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = endpoint.startsWith("https://")
    ? endpoint
    : `https://api.github.com${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: "application/vnd.github.v3+json",
      "X-GitHub-Api-Version": "2022-11-28",
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.text()
    throw new Error(`GitHub API error: ${response.status} ${error}`)
  }
  
  return response
}

/**
 * List all workflows in the repository
 */
export async function listWorkflows(accessToken: string): Promise<Workflow[]> {
  const response = await githubFetch(
    `/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows`,
    accessToken
  )
  
  const data = await response.json()
  return data.workflows
}

/**
 * Get recent workflow runs
 */
export async function getWorkflowRuns(
  accessToken: string,
  workflowId?: number,
  limit = 10
): Promise<WorkflowRun[]> {
  const endpoint = workflowId
    ? `/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${workflowId}/runs`
    : `/repos/${REPO_OWNER}/${REPO_NAME}/actions/runs`
  
  const response = await githubFetch(
    `${endpoint}?per_page=${limit}`,
    accessToken
  )
  
  const data = await response.json()
  return data.workflow_runs
}

/**
 * Trigger a workflow dispatch event
 */
export async function triggerWorkflow(
  accessToken: string,
  workflowId: string | number,
  ref = "master",
  inputs: Record<string, string> = {}
): Promise<void> {
  await githubFetch(
    `/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${workflowId}/dispatches`,
    accessToken,
    {
      method: "POST",
      body: JSON.stringify({
        ref,
        inputs,
      }),
    }
  )
}

/**
 * Get files in a directory
 */
export async function listFiles(
  accessToken: string,
  path: string
): Promise<RepoFile[]> {
  const response = await githubFetch(
    `/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`,
    accessToken
  )
  
  return response.json()
}

/**
 * Get file content
 */
export async function getFileContent(
  accessToken: string,
  path: string
): Promise<{ content: string; sha: string }> {
  const response = await githubFetch(
    `/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`,
    accessToken
  )
  
  const data = await response.json()
  const content = atob(data.content)
  
  return {
    content,
    sha: data.sha,
  }
}

/**
 * Update file content (creates commit)
 */
export async function updateFile(
  accessToken: string,
  path: string,
  content: string,
  message: string,
  sha?: string
): Promise<void> {
  // Get current SHA if not provided
  let fileSha = sha
  if (!fileSha) {
    try {
      const existing = await getFileContent(accessToken, path)
      fileSha = existing.sha
    } catch {
      // File doesn't exist, will create new
    }
  }
  
  await githubFetch(
    `/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`,
    accessToken,
    {
      method: "PUT",
      body: JSON.stringify({
        message,
        content: btoa(content),
        sha: fileSha,
        branch: "master",
      }),
    }
  )
}

/**
 * Get repository info
 */
export async function getRepository(accessToken: string) {
  const response = await githubFetch(
    `/repos/${REPO_OWNER}/${REPO_NAME}`,
    accessToken
  )
  
  return response.json()
}

/**
 * Get health.json from GitHub Pages
 */
export async function getHealthStatus(): Promise<{
  status: string
  book_count: number
  newest_book: string | null
  oldest_book: string | null
  last_update: string
  total_size_mb: number
  books: Array<{
    filename: string
    date: string
    size_bytes: number
    title: string
  }>
}> {
  const response = await fetch(
    `https://${REPO_OWNER.toLowerCase()}.github.io/${REPO_NAME}/health.json`,
    { next: { revalidate: 60 } } // Cache for 60 seconds
  )
  
  if (!response.ok) {
    throw new Error("Failed to fetch health status")
  }
  
  return response.json()
}
