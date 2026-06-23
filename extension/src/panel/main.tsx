import {
  ApiError,
  clearSession,
  configureApi,
  isAuthFailure,
  resolveApiBaseUrl,
} from "@rag-agent/shared"
import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { chromeStorageAdapter } from "../storage/chrome-storage"
import { App } from "./App"
import "./styles/widget.css"

const apiBaseUrl = resolveApiBaseUrl(import.meta.env.VITE_API_URL)

configureApi({
  baseUrl: apiBaseUrl,
  storage: chromeStorageAdapter,
})

const handleApiError = (error: Error) => {
  if (!(error instanceof ApiError)) return
  if (!isAuthFailure(error)) return
  if (!error.url.includes("/users/me")) return
  void clearSession()
}

const queryClient = new QueryClient({
  queryCache: new QueryCache({ onError: handleApiError }),
  mutationCache: new MutationCache({ onError: handleApiError }),
})

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App apiBaseUrl={apiBaseUrl} />
    </QueryClientProvider>
  </StrictMode>,
)
