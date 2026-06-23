import type { StorageAdapter } from "./types"

export const localStorageAdapter: StorageAdapter = {
  getItem(key: string) {
    return localStorage.getItem(key)
  },
  setItem(key: string, value: string) {
    localStorage.setItem(key, value)
  },
  removeItem(key: string) {
    localStorage.removeItem(key)
  },
}
