export interface StorageAdapter {
  getItem(key: string): Promise<string | null> | string | null
  setItem(key: string, value: string): Promise<void> | void
  removeItem(key: string): Promise<void> | void
}

export const ACCESS_TOKEN_KEY = "access_token"
export const SELECTED_CUSTOMER_KEY = "selected_customer_id"
