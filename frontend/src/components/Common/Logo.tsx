import { Link } from "@tanstack/react-router"

import { APP_NAME } from "@/lib/brand"
import { cn } from "@/lib/utils"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

function LogoMark({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "font-retro-display text-primary retro-glow-cyan select-none",
        className,
      )}
      aria-hidden
    >
      Δ
    </span>
  )
}

function LogoFull({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "font-retro-brand tracking-tight select-none leading-none",
        className,
      )}
    >
      <span className="text-foreground retro-logo-greek">Διάβασ</span>
      <span className="text-primary retro-glow-cyan">ΑΙ</span>
    </span>
  )
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const content =
    variant === "responsive" ? (
      <>
        <LogoFull
          className={cn(
            "text-lg sm:text-xl group-data-[collapsible=icon]:hidden",
            className,
          )}
        />
        <LogoMark
          className={cn(
            "text-xl hidden group-data-[collapsible=icon]:block",
            className,
          )}
        />
      </>
    ) : variant === "full" ? (
      <LogoFull className={cn("text-lg sm:text-xl", className)} />
    ) : (
      <LogoMark className={cn("text-xl", className)} />
    )

  if (!asLink) {
    return (
      <div role="img" aria-label={APP_NAME}>
        {content}
      </div>
    )
  }

  return (
    <Link to="/" aria-label={APP_NAME}>
      {content}
    </Link>
  )
}
