import type { UserPublic } from "../client"

export const VIEWER_EXTENSION_FEATURES = {
  chat: true,
  customerSelect: true,
  documents: false,
  admin: false,
  settings: false,
} as const

export function canManageDocuments(
  user: UserPublic | null | undefined,
): boolean {
  return !!user && (user.is_superuser || user.role === "moderator")
}

export function canAccessDocuments(
  user: UserPublic | null | undefined,
): boolean {
  return canManageDocuments(user)
}

export function canShowHeaderCustomerSelect(
  user: UserPublic | null | undefined,
): boolean {
  return canManageDocuments(user)
}
