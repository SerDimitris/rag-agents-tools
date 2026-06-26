import type { DocumentPublic } from "@rag-agent/shared"
import { OpenAPI } from "@rag-agent/shared"

export async function uploadDocument(
  file: File,
  customerId: string,
  title?: string,
): Promise<DocumentPublic> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("customer_id", customerId)
  if (title) {
    formData.append("title", title)
  }

  const token = localStorage.getItem("access_token")
  const headers: Record<string, string> = {}
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${OpenAPI.BASE}/api/v1/documents/upload`, {
    method: "POST",
    headers,
    body: formData,
  })

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Upload failed" }))
    throw new Error(
      typeof error.detail === "string"
        ? error.detail
        : "Failed to upload document",
    )
  }

  return response.json()
}
