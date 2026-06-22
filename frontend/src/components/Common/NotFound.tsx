import { Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

const NotFound = () => {
  return (
    <div
      className="flex min-h-screen items-center justify-center flex-col p-4 retro-cabinet-bg"
      data-testid="not-found"
    >
      <div className="flex items-center z-10">
        <div className="flex flex-col ml-4 items-center justify-center p-4">
          <span className="text-4xl md:text-6xl font-retro-display text-accent retro-glow-magenta leading-none mb-4">
            404
          </span>
          <span className="text-xs md:text-sm font-retro-display text-primary retro-glow-cyan mb-2">
            GAME OVER
          </span>
        </div>
      </div>

      <p className="text-sm font-retro-body text-muted-foreground mb-4 text-center z-10">
        Level not found. Wrong warp zone?
      </p>
      <div className="z-10">
        <Link to="/">
          <Button className="mt-4">CONTINUE?</Button>
        </Link>
      </div>
    </div>
  )
}

export default NotFound
