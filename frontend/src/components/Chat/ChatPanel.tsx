import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Loader2, Send } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import { ChatService, type ChatMessagePublic } from "@/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

function getChatMessagesQueryOptions() {
  return {
    queryKey: ["chat-messages"],
    queryFn: () => ChatService.readChatMessages({ skip: 0, limit: 100 }),
  }
}

function ChatBubble({ message }: { message: ChatMessagePublic }) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-none border-2 px-4 py-2 text-sm font-retro-body whitespace-pre-wrap retro-pixel-shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground border-primary/50"
            : "bg-muted text-foreground border-border",
        )}
      >
        {message.content}
      </div>
    </div>
  )
}

export function ChatPanel() {
  const [input, setInput] = useState("")
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data, isLoading } = useQuery(getChatMessagesQueryOptions())

  const mutation = useMutation({
    mutationFn: (content: string) =>
      ChatService.sendChatMessage({ requestBody: { content } }),
    onSuccess: () => {
      setInput("")
      queryClient.invalidateQueries({ queryKey: ["chat-messages"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [data?.data.length, mutation.isPending])

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || mutation.isPending) return
    mutation.mutate(trimmed)
  }

  return (
    <div className="flex h-[calc(100vh-12rem)] flex-col rounded-none border-2 bg-card retro-pixel-shadow">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
        {isLoading ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Loading conversation...
          </div>
        ) : data?.data.length ? (
          data.data.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))
        ) : (
          <div className="flex h-full items-center justify-center text-center text-muted-foreground">
            <div>
              <p className="font-medium text-foreground">
                Ask about your uploaded documents
              </p>
              <p className="mt-1 text-sm">
                The assistant answers using extracted content from completed
                documents.
              </p>
            </div>
          </div>
        )}
        {mutation.isPending && (
          <div className="flex justify-start">
            <div className="rounded-lg bg-muted px-4 py-2 text-sm text-muted-foreground">
              <Loader2 className="mr-2 inline h-4 w-4 animate-spin" />
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 border-t p-4"
      >
        <Input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={mutation.isPending}
        />
        <Button type="submit" size="icon" disabled={mutation.isPending || !input.trim()}>
          <Send className="h-4 w-4" />
          <span className="sr-only">Send</span>
        </Button>
      </form>
    </div>
  )
}
