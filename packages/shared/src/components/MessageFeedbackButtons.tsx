import { useState, type FormEvent } from "react"

import type {
  ChatMessagePublic,
  FeedbackRating,
  FeedbackReason,
} from "../client"

export type MessageFeedbackPayload = {
  messageId: string
  rating: FeedbackRating
  reason?: FeedbackReason
  comment?: string
}

type MessageFeedbackButtonsProps = {
  message: ChatMessagePublic
  onFeedback: (payload: MessageFeedbackPayload) => void
  isPending?: boolean
  className?: string
  buttonClassName?: string
  activeClassName?: string
  formClassName?: string
}

const FEEDBACK_REASONS: { value: FeedbackReason; label: string }[] = [
  { value: "wrong", label: "Wrong information" },
  { value: "incomplete", label: "Incomplete answer" },
  { value: "outdated", label: "Outdated information" },
  { value: "off_topic", label: "Off topic" },
  { value: "other", label: "Other" },
]

export function MessageFeedbackButtons({
  message,
  onFeedback,
  isPending = false,
  className = "",
  buttonClassName = "",
  activeClassName = "",
  formClassName = "",
}: MessageFeedbackButtonsProps) {
  const [showNegativeForm, setShowNegativeForm] = useState(false)
  const [reason, setReason] = useState<FeedbackReason>("wrong")
  const [comment, setComment] = useState("")

  if (message.role !== "assistant" || message.response_kind === "clarification") {
    return null
  }

  const isPositive = message.feedback_rating === "positive"
  const isNegative = message.feedback_rating === "negative"

  const handlePositive = () => {
    setShowNegativeForm(false)
    onFeedback({ messageId: message.id, rating: "positive" })
  }

  const handleNegativeClick = () => {
    if (isNegative) {
      setShowNegativeForm((open) => !open)
      return
    }
    setShowNegativeForm(true)
  }

  const handleNegativeSubmit = (event: FormEvent) => {
    event.preventDefault()
    onFeedback({
      messageId: message.id,
      rating: "negative",
      reason,
      comment: comment.trim() || undefined,
    })
    setShowNegativeForm(false)
  }

  return (
    <div className={className}>
      <div role="group" aria-label="Rate this answer" className="flex gap-1">
        <button
          type="button"
          className={`${buttonClassName} ${isPositive ? activeClassName : ""}`.trim()}
          aria-label="Helpful"
          aria-pressed={isPositive}
          disabled={isPending}
          onClick={handlePositive}
        >
          👍
        </button>
        <button
          type="button"
          className={`${buttonClassName} ${isNegative ? activeClassName : ""}`.trim()}
          aria-label="Not helpful"
          aria-pressed={isNegative}
          disabled={isPending}
          onClick={handleNegativeClick}
        >
          👎
        </button>
      </div>

      {showNegativeForm && (
        <form
          className={formClassName}
          onSubmit={handleNegativeSubmit}
          aria-label="Tell us what went wrong"
        >
          <label className="block text-xs">
            What was wrong?
            <select
              className="mt-1 block w-full"
              value={reason}
              disabled={isPending}
              onChange={(event) => setReason(event.target.value as FeedbackReason)}
            >
              {FEEDBACK_REASONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-2 block text-xs">
            Additional details (optional)
            <textarea
              className="mt-1 block w-full resize-y"
              rows={2}
              maxLength={2000}
              value={comment}
              disabled={isPending}
              onChange={(event) => setComment(event.target.value)}
              placeholder="Help us improve this answer"
            />
          </label>
          <div className="mt-2 flex gap-2">
            <button type="submit" disabled={isPending}>
              Submit feedback
            </button>
            <button
              type="button"
              disabled={isPending}
              onClick={() => setShowNegativeForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
