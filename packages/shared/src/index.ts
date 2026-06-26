export { configureApi, getStorageAdapter, resolveApiBaseUrl } from "./api/configure-api"
export { CustomerSelect } from "./components/CustomerSelect"
export { MessageFeedbackButtons } from "./components/MessageFeedbackButtons"
export { CustomerProvider, useCustomer } from "./contexts/CustomerContext"
export { useAuthSession, clearSession } from "./hooks/useAuthSession"
export {
  getChatMessagesQueryOptions,
  useChatMessages,
  useSendChatMessage,
  useSubmitMessageFeedback,
  type MessageFeedbackInput,
} from "./hooks/useChat"
export type { MessageFeedbackPayload } from "./components/MessageFeedbackButtons"
export {
  VIEWER_EXTENSION_FEATURES,
  canManageDocuments,
  canAccessDocuments,
  canShowHeaderCustomerSelect,
} from "./lib/roles"
export { localStorageAdapter } from "./storage/local-storage"
export {
  ACCESS_TOKEN_KEY,
  SELECTED_CUSTOMER_KEY,
  type StorageAdapter,
} from "./storage/types"
export { handleError, isAuthFailure } from "./utils/handleError"

export {
  ApiError,
  CancelablePromise,
  CancelError,
  OpenAPI,
  type OpenAPIConfig,
} from "./client"
export * from "./client/sdk.gen"
export * from "./client/types.gen"
