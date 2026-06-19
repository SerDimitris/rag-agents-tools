import type { UserPublic } from "@/client"

export function canManageDocuments(
  user: UserPublic | null | undefined,
): boolean {
  return !!user && (user.is_superuser || user.role === "moderator")
}
