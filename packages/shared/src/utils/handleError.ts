import { AxiosError } from "axios"
import { ApiError } from "../client"

function extractErrorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    if (err.code === "ECONNABORTED") {
      return "Request timed out. Check that the API is running and reachable."
    }
    if (err.message === "Network Error") {
      return "Cannot reach the API. Confirm VITE_API_URL and host_permissions match your backend URL."
    }
    return err.message
  }

  if (err instanceof ApiError) {
    const errDetail = (err.body as { detail?: string | { msg: string }[] })?.detail
    if (Array.isArray(errDetail) && errDetail.length > 0) {
      return errDetail[0].msg
    }
    if (typeof errDetail === "string") {
      return errDetail
    }
    return err.message || "Something went wrong."
  }

  if (err instanceof Error) {
    return err.message
  }

  return "Something went wrong."
}

export function handleError(
  showError: (msg: string) => void,
  err: unknown,
) {
  showError(extractErrorMessage(err))
}

export function isAuthFailure(error: ApiError): boolean {
  return (
    [401, 403].includes(error.status) ||
    (error.status === 404 &&
      (error.url.includes("/users/me") ||
        (typeof error.body === "object" &&
          error.body !== null &&
          "detail" in error.body &&
          error.body.detail === "User not found")))
  )
}
