import { createFileRoute } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"
import { pageTitle } from "@/lib/brand"
export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: pageTitle("Dashboard"),
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <div>
      <div>
        <h1 className="text-sm sm:text-base truncate max-w-sm text-primary retro-glow-cyan">
          USER: {currentUser?.full_name || currentUser?.email}
        </h1>
        <p className="text-muted-foreground font-retro-body mt-2">
          Welcome back — press start to continue
          <span className="retro-blink">_</span>
        </p>
      </div>
    </div>
  )
}
