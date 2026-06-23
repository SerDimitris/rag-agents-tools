import type { StorageAdapter } from "@rag-agent/shared"

export const chromeStorageAdapter: StorageAdapter = {
  async getItem(key: string) {
    const result = await chrome.storage.local.get(key)
    const value = result[key]
    return typeof value === "string" ? value : null
  },
  async setItem(key: string, value: string) {
    await chrome.storage.local.set({ [key]: value })
  },
  async removeItem(key: string) {
    await chrome.storage.local.remove(key)
  },
}
