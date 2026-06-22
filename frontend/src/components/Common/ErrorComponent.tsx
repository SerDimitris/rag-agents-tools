import { Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

const ErrorComponent = () => {
  return (
    <div
      className="flex min-h-screen items-center justify-center flex-col p-4 retro-cabinet-bg"
      data-testid="error-component"
    >
      <div className="flex items-center z-10">
        <div className="flex flex-col ml-4 items-center justify-center p-4">
          <span className="text-3xl md:text-5xl font-retro-display text-destructive retro-glow-magenta leading-none mb-4">
            ERROR
          </span>
          <span className="text-xs md:text-sm font-retro-display text-primary retro-glow-cyan mb-2">
            CRITICAL HIT
          </span>
        </div>
      </div>

      <p className="text-sm font-retro-body text-muted-foreground mb-4 text-center z-10">
        Something glitched. Try again?
      </p>
      <Link to="/">
        <Button>TRY AGAIN</Button>
      </Link>
    </div>
  )
}

export default ErrorComponent
