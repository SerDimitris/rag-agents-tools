import { OpenAPI } from "../client"
import { ACCESS_TOKEN_KEY, type StorageAdapter } from "../storage/types"

let activeStorage: StorageAdapter | null = null

export function getStorageAdapter(): StorageAdapter {
  if (!activeStorage) {
    throw new Error("API not configured. Call configureApi() first.")
  }
  return activeStorage
}

export function configureApi(options: {
  baseUrl: string
  storage: StorageAdapter
  requestTimeoutMs?: number
}) {
  activeStorage = options.storage
  const normalizedBaseUrl = options.baseUrl.trim().replace(/\/$/, "")
  OpenAPI.BASE = normalizedBaseUrl || "http://localhost:8000"
  OpenAPI.TOKEN = async () => {
    const token = await options.storage.getItem(ACCESS_TOKEN_KEY)
    return token ?? ""
  }

  const timeout = options.requestTimeoutMs ?? 15_000
  OpenAPI.interceptors.request.use((requestConfig) => ({
    ...requestConfig,
    timeout,
  }))
}

export function resolveApiBaseUrl(
  configuredUrl: string | undefined,
  fallback = "http://localhost:8000",
): string {
  const trimmed = configuredUrl?.trim()
  return (trimmed || fallback).replace(/\/$/, "")
}
