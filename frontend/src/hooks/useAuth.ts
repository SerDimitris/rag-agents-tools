import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import {
  ACCESS_TOKEN_KEY,
  type ApiError,
  type UserRegister,
  useAuthSession,
  UsersService,
} from "@rag-agent/shared"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

const isLoggedIn = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY) !== null
}

const useAuth = () => {
  const navigate = useNavigate()
  const { showErrorToast } = useCustomToast()

  const session = useAuthSession({
    onLoginSuccess: () => navigate({ to: "/" }),
    onLogout: () => navigate({ to: "/login" }),
    onError: showErrorToast,
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: (err: Error) => {
      handleError.call(showErrorToast, err as ApiError)
    },
  })

  return {
    signUpMutation,
    loginMutation: session.loginMutation,
    logout: session.logout,
    user: session.user,
  }
}

export { isLoggedIn }
export default useAuth
