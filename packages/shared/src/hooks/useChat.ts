import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { ChatService } from "../client"

export function getChatMessagesQueryOptions(customerId: string) {
  return {
    queryKey: ["chat-messages", customerId],
    queryFn: () =>
      ChatService.readChatMessages({ customerId, skip: 0, limit: 100 }),
  }
}

export function useChatMessages(customerId: string | null) {
  return useQuery({
    ...getChatMessagesQueryOptions(customerId ?? ""),
    enabled: Boolean(customerId),
  })
}

export function useSendChatMessage(
  customerId: string | null,
  options?: { onSuccess?: () => void; onError?: (message: string) => void },
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (content: string) => {
      if (!customerId) {
        throw new Error("Please select a customer first")
      }
      return ChatService.sendChatMessage({
        requestBody: { content, customer_id: customerId },
      })
    },
    onSuccess: () => {
      if (customerId) {
        queryClient.invalidateQueries({ queryKey: ["chat-messages", customerId] })
      }
      options?.onSuccess?.()
    },
    onError: (err) => {
      options?.onError?.(
        err instanceof Error ? err.message : "Failed to send message",
      )
    },
  })
}
