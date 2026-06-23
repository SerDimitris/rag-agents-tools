import {
  type ChatMessagePublic,
  CustomerSelect,
  useChatMessages,
  useCustomer,
  useSendChatMessage,
} from "@rag-agent/shared"
import { useEffect, useRef, useState } from "react"

type ChatViewProps = {
  userEmail: string
  onLogout: () => void
}

function ChatBubble({ message }: { message: ChatMessagePublic }) {
  const isUser = message.role === "user"

  return (
    <div className={`widget-bubble-row ${isUser ? "is-user" : "is-assistant"}`}>
      <div className={`widget-bubble ${isUser ? "is-user" : "is-assistant"}`}>
        {message.content}
      </div>
    </div>
  )
}

export function ChatView({ userEmail, onLogout }: ChatViewProps) {
  const [input, setInput] = useState("")
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const { customerId, selectedCustomer } = useCustomer()

  const { data, isLoading } = useChatMessages(customerId)

  const mutation = useSendChatMessage(customerId, {
    onSuccess: () => {
      setInput("")
      setErrorMessage(null)
    },
    onError: setErrorMessage,
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
    if (!trimmed || mutation.isPending || !customerId) return
    mutation.mutate(trimmed)
  }

  return (
    <div className="widget-shell widget-chat">
      <header className="widget-header widget-chat-header">
        <div>
          <h1 className="widget-title">RAG Chat</h1>
          <p className="widget-subtitle">{userEmail}</p>
        </div>
        <button className="widget-link-button" type="button" onClick={onLogout}>
          Log out
        </button>
      </header>

      <div className="widget-customer-bar">
        <CustomerSelect
          className="widget-customer-select"
          selectClassName="widget-select"
          labelClassName="widget-label-text"
        />
      </div>

      {!customerId ? (
        <div className="widget-center widget-empty">
          <p className="widget-muted">Select a customer to start chatting.</p>
        </div>
      ) : (
        <>
          <div ref={scrollRef} className="widget-messages">
            {isLoading ? (
              <p className="widget-muted widget-center">Loading conversation...</p>
            ) : data?.data.length ? (
              data.data.map((message) => (
                <ChatBubble key={message.id} message={message} />
              ))
            ) : (
              <div className="widget-center widget-empty">
                <p className="widget-strong">
                  Ask about {selectedCustomer?.name}&apos;s documents
                </p>
                <p className="widget-muted">
                  Answers use uploaded documents for this customer only.
                </p>
              </div>
            )}
            {mutation.isPending && (
              <div className="widget-bubble-row is-assistant">
                <div className="widget-bubble is-assistant widget-thinking">
                  Thinking...
                </div>
              </div>
            )}
          </div>

          {errorMessage && <p className="widget-error widget-inline-error">{errorMessage}</p>}

          <form className="widget-composer" onSubmit={handleSubmit}>
            <input
              className="widget-input widget-composer-input"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={`Ask about ${selectedCustomer?.name ?? "this customer"}...`}
              disabled={mutation.isPending}
            />
            <button
              className="widget-button widget-send-button"
              type="submit"
              disabled={mutation.isPending || !input.trim()}
            >
              Send
            </button>
          </form>
        </>
      )}
    </div>
  )
}
