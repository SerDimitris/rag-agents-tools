import { createFileRoute } from "@tanstack/react-router"

import { ChatPanel } from "@/components/Chat/ChatPanel"
import { pageTitle } from "@/lib/brand"

export const Route = createFileRoute("/_layout/chat")({
  component: Chat,
  head: () => ({
    meta: [
      {
        title: pageTitle("Chat"),
      },
    ],
  }),
})

function Chat() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-sm sm:text-base text-primary retro-glow-cyan">CHAT TERMINAL</h1>
        <p className="text-muted-foreground font-retro-body mt-2">
          Query your document knowledge base
        </p>
      </div>
      <ChatPanel />
    </div>
  )
}
