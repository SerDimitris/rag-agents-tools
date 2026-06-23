import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useCallback, useEffect, useRef, useState } from "react"

import { getStorageAdapter } from "../api/configure-api"
import {
  ApiError,
  type Body_login_login_access_token as AccessToken,
  LoginService,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "../client"
import { ACCESS_TOKEN_KEY } from "../storage/types"
import { handleError, isAuthFailure } from "../utils/handleError"

async function checkLoggedIn(): Promise<boolean> {
  const storage = getStorageAdapter()
  const token = await storage.getItem(ACCESS_TOKEN_KEY)
  return token !== null && token !== ""
}

export function useAuthSession(options?: {
  onLoginSuccess?: () => void
  onLogout?: () => void
  onError?: (message: string) => void
}) {
  const queryClient = useQueryClient()
  const storage = getStorageAdapter()
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null)
  const optionsRef = useRef(options)
  optionsRef.current = options

  useEffect(() => {
    void checkLoggedIn().then(setLoggedIn)
  }, [])

  const { data: user, isLoading: userLoading, isError, error } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    enabled: loggedIn === true,
  })

  useEffect(() => {
    if (!isError || !(error instanceof ApiError) || !isAuthFailure(error)) {
      return
    }

    void (async () => {
      await storage.removeItem(ACCESS_TOKEN_KEY)
      setLoggedIn(false)
      queryClient.setQueryData(["currentUser"], null)
      optionsRef.current?.onLogout?.()
    })()
  }, [isError, error, storage, queryClient])

  const showError = useCallback(
    (message: string) => {
      optionsRef.current?.onError?.(message)
    },
    [],
  )

  const login = useCallback(
    async (data: AccessToken) => {
      const response = await LoginService.loginAccessToken({ formData: data })
      await storage.setItem(ACCESS_TOKEN_KEY, response.access_token)
      setLoggedIn(true)
      void queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      optionsRef.current?.onLoginSuccess?.()
    },
    [storage, queryClient],
  )

  const loginMutation = useMutation({
    mutationFn: login,
    onError: (err) => handleError(showError, err),
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),
    onError: (err) => handleError(showError, err),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const logout = useCallback(async () => {
    await storage.removeItem(ACCESS_TOKEN_KEY)
    setLoggedIn(false)
    queryClient.setQueryData(["currentUser"], null)
    queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    optionsRef.current?.onLogout?.()
  }, [storage, queryClient])

  return {
    user: user ?? null,
    isLoggedIn: loggedIn === true,
    isAuthReady: loggedIn !== null,
    isLoading: loggedIn === null || (loggedIn && userLoading),
    login,
    loginMutation,
    signUpMutation,
    logout,
  }
}

export async function clearSession(): Promise<void> {
  const storage = getStorageAdapter()
  await storage.removeItem(ACCESS_TOKEN_KEY)
}
