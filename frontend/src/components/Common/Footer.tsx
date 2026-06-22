import { APP_NAME } from "@/lib/brand"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-primary/20 py-4 px-6 retro-pixel-border-t">
      <div className="flex flex-col items-center justify-center gap-1 text-center">
        <p className="font-retro-display text-[10px] sm:text-xs text-primary retro-glow-cyan tracking-wider">
          {APP_NAME}
        </p>
        <p className="text-muted-foreground text-xs font-retro-body">
          © {currentYear} · INSERT COIN TO CONTINUE
        </p>
      </div>
    </footer>
  )
}
