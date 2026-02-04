import { redirect } from "next/navigation"
import { DashboardNav } from "@/components/dashboard/nav"

async function getSessionSafe() {
  try {
    const { getSession } = await import("@/lib/auth")
    return await getSession()
  } catch {
    return null
  }
}

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getSessionSafe()
  
  if (!session) {
    redirect("/login")
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      <DashboardNav user={session.user} />
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  )
}
