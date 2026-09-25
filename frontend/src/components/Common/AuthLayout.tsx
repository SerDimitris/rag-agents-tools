import { Appearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import { RetroStarfield } from "@/components/Common/RetroStarfield"
import { Footer } from "./Footer"

interface AuthLayoutProps {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="dark retro-cabinet-bg retro-scanlines relative hidden overflow-hidden lg:flex lg:flex-col lg:items-center lg:justify-center lg:gap-6">
        <RetroStarfield />
        <Logo
          variant="full"
          className="text-2xl sm:text-3xl z-10"
          asLink={false}
        />
        <p className="font-retro-display text-[9px] sm:text-[10px] text-primary/80 retro-glow-cyan z-10 text-center px-6 tracking-wider">
          READ · LEARN · LEVEL UP
        </p>
      </div>
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-end">
          <Appearance />
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">{children}</div>
        </div>
        <Footer />
      </div>
    </div>
  )
}
