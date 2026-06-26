import { Loader2, Send } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import {
  type ChatMessagePublic,
  type MessageFeedbackPayload,
  MessageFeedbackButtons,
  useChatMessages,
  useCustomer,
  useSendChatMessage,
  useSubmitMessageFeedback,
} from "@rag-agent/shared"
import { Button } from "@/components/ui/button"
import { CustomerSelect } from "@/components/Customers/CustomerSelect"
import { Input } from "@/components/ui/input"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { canShowHeaderCustomerSelect } from "@/lib/roles"
import { cn } from "@/lib/utils"

type ChatBubbleProps = {
  message: ChatMessagePublic
  onFeedback: (payload: MessageFeedbackPayload) => void
  feedbackPending: boolean
}

function ChatBubble({ message, onFeedback, feedbackPending }: ChatBubbleProps) {
  const isUser = message.role === "user"
  const isClarification =
    !isUser && message.response_kind === "clarification"

  return (
    <div className={cn("flex flex-col gap-1", isUser ? "items-end" : "items-start")}>
      {isClarification && (
        <p className="max-w-[80%] text-xs font-medium text-amber-700 dark:text-amber-400">
          Clarification needed
        </p>
      )}
      <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
        <div
          className={cn(
            "max-w-[80%] rounded-none border-2 px-4 py-2 text-sm font-retro-body whitespace-pre-wrap retro-pixel-shadow-sm",
            isUser
              ? "bg-primary text-primary-foreground border-primary/50"
              : isClarification
                ? "bg-amber-50 text-foreground border-amber-300 dark:bg-amber-950/40 dark:border-amber-700"
                : "bg-muted text-foreground border-border",
          )}
        >
          {message.content}
        </div>
      </div>
      {!isUser && message.source_titles && message.source_titles.length > 0 && (
        <p className="max-w-[80%] text-xs text-muted-foreground">
          Sources: {message.source_titles.join(", ")}
        </p>
      )}
      {!isUser && (
        <MessageFeedbackButtons
          message={message}
          onFeedback={onFeedback}
          isPending={feedbackPending}
          className="flex max-w-[80%] flex-col gap-2"
          buttonClassName="rounded-none border px-2 py-1 text-xs text-muted-foreground transition hover:bg-muted disabled:opacity-50"
          activeClassName="border-primary bg-primary/10 text-foreground"
          formClassName="rounded-none border bg-card p-3 text-xs retro-pixel-shadow-sm"
        />
      )}
    </div>
  )
}

export function ChatPanel() {
  const [input, setInput] = useState("")
  const { showErrorToast } = useCustomToast()
  const scrollRef = useRef<HTMLDivElement>(null)
  const { user } = useAuth()
  const { customerId, selectedCustomer } = useCustomer()
  const showChatCustomerSelect = !canShowHeaderCustomerSelect(user)

  const { data, isLoading } = useChatMessages(customerId)

  const mutation = useSendChatMessage(customerId, {
    onSuccess: () => setInput(""),
    onError: (message) => showErrorToast(message),
  })

  const feedbackMutation = useSubmitMessageFeedback(customerId)

  const handleFeedback = (payload: MessageFeedbackPayload) => {
    feedbackMutation.mutate(payload, {
      onError: (err) =>
        showErrorToast(
          err instanceof Error ? err.message : "Failed to submit feedback",
        ),
    })
  }

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [data?.data.length, mutation.isPending])

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || mutation.isPending || !customerId) return
    mutation.mutate(trimmed)
  }

  if (!customerId) {
    return (
      <div className="flex h-[calc(100vh-12rem)] flex-col items-center justify-center gap-4 rounded-none border-2 bg-card retro-pixel-shadow">
        {showChatCustomerSelect && <CustomerSelect />}
        <p className="text-muted-foreground">Select a customer to start chatting.</p>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-12rem)] flex-col rounded-none border-2 bg-card retro-pixel-shadow">
      <div className="flex items-center justify-between border-b px-4 py-2 text-sm text-muted-foreground">
        {showChatCustomerSelect ? (
          <CustomerSelect />
        ) : (
          <span>
            Chatting for{" "}
            <span className="font-medium text-foreground">{selectedCustomer?.name}</span>
          </span>
        )}
      </div>
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
        {isLoading ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Loading conversation...
          </div>
        ) : data?.data.length ? (
          data.data.map((message) => (
            <ChatBubble
              key={message.id}
              message={message}
              onFeedback={handleFeedback}
              feedbackPending={feedbackMutation.isPending}
            />
          ))
        ) : (
          <div className="flex h-full items-center justify-center text-center text-muted-foreground">
            <div>
              <p className="font-medium text-foreground">
                Ask about {selectedCustomer?.name}&apos;s documents
              </p>
              <p className="mt-1 text-sm">
                The assistant answers using extracted content from completed
                documents for this customer only.
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
          placeholder={`Ask a question about ${selectedCustomer?.name ?? "this customer"}'s documents...`}
          disabled={mutation.isPending || !customerId}
        />
        <Button
          type="submit"
          size="icon"
          disabled={mutation.isPending || !input.trim() || !customerId}
        >
          <Send className="h-4 w-4" />
          <span className="sr-only">Send</span>
        </Button>
      </form>
    </div>
  )
}
