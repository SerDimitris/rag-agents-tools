import type { Body_login_login_access_token as AccessToken } from "@rag-agent/shared"
import { useState } from "react"

type LoginViewProps = {
  apiBaseUrl: string
  errorMessage: string | null
  isPending: boolean
  onClearError: () => void
  onSubmit: (credentials: AccessToken) => void
}

export function LoginView({
  apiBaseUrl,
  errorMessage,
  isPending,
  onClearError,
  onSubmit,
}: LoginViewProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    onClearError()
    onSubmit({
      username: email,
      password,
      grant_type: "password",
      scope: "",
      client_id: "",
      client_secret: "",
    })
  }

  return (
    <div className="widget-shell">
      <header className="widget-header">
        <h1 className="widget-title">RAG Chat</h1>
        <p className="widget-subtitle">Sign in to chat with the assistant</p>
      </header>

      <form className="widget-form" onSubmit={handleSubmit}>
        <label className="widget-label">
          Email
          <input
            className="widget-input"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>

        <label className="widget-label">
          Password
          <input
            className="widget-input"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>

        {errorMessage && <p className="widget-error">{errorMessage}</p>}

        <button className="widget-button" type="submit" disabled={isPending}>
          {isPending ? "Signing in..." : "Sign in"}
        </button>

        <p className="widget-muted widget-api-hint">API: {apiBaseUrl}</p>
      </form>
    </div>
  )
}
