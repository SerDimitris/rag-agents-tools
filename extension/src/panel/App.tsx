import { CustomerProvider, useAuthSession } from "@rag-agent/shared"
import { useState } from "react"
import { ChatView } from "./views/ChatView"
import { LoginView } from "./views/LoginView"

type AppProps = {
  apiBaseUrl: string
}

export function App({ apiBaseUrl }: AppProps) {
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const { isLoggedIn, isAuthReady, isLoading, loginMutation, logout, user } =
    useAuthSession({
      onError: setErrorMessage,
      onLogout: () => setErrorMessage(null),
    })

  if (!isAuthReady || (isLoggedIn && isLoading)) {
    return (
      <div className="widget-shell widget-center">
        <p className="widget-muted">Loading...</p>
      </div>
    )
  }

  if (!isLoggedIn) {
    return (
      <LoginView
        apiBaseUrl={apiBaseUrl}
        errorMessage={errorMessage}
        isPending={loginMutation.isPending}
        onClearError={() => setErrorMessage(null)}
        onSubmit={(credentials) => {
          setErrorMessage(null)
          loginMutation.mutate(credentials)
        }}
      />
    )
  }

  return (
    <CustomerProvider enabled={isLoggedIn}>
      <ChatView
        userEmail={user?.email ?? ""}
        onLogout={() => {
          void logout()
        }}
      />
    </CustomerProvider>
  )
}
