import { FileText, Home, MessageSquare, Users } from "lucide-react"
import {
  canAccessDocuments,
  canManageDocuments,
  canShowHeaderCustomerSelect,
  type UserPublic,
} from "@rag-agent/shared"
import type { Item } from "@/components/Sidebar/Main"

export {
  canManageDocuments,
  canAccessDocuments,
  canShowHeaderCustomerSelect,
}

export function getNavItems(user: UserPublic | null | undefined): Item[] {
  const items: Item[] = [{ icon: Home, title: "Dashboard", path: "/" }]

  if (canAccessDocuments(user)) {
    items.push({ icon: FileText, title: "Documents", path: "/documents" })
  }

  items.push({ icon: MessageSquare, title: "Chat", path: "/chat" })

  if (user?.is_superuser) {
    items.push({ icon: Users, title: "Admin", path: "/admin" })
  }

  return items
}
