import { useQuery } from "@tanstack/react-query"
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react"

import { CustomersService, type CustomerPublic } from "@/client"

const STORAGE_KEY = "selected_customer_id"

type CustomerContextValue = {
  customers: CustomerPublic[]
  customerId: string | null
  selectedCustomer: CustomerPublic | null
  setCustomerId: (customerId: string) => void
  isLoading: boolean
}

const CustomerContext = createContext<CustomerContextValue | null>(null)

function getCustomersQueryOptions() {
  return {
    queryKey: ["customers"],
    queryFn: () => CustomersService.readCustomers({ skip: 0, limit: 100 }),
  }
}

export function CustomerProvider({ children }: { children: React.ReactNode }) {
  const { data, isLoading } = useQuery(getCustomersQueryOptions())
  const customers = data?.data ?? []

  const [customerId, setCustomerIdState] = useState<string | null>(() =>
    localStorage.getItem(STORAGE_KEY),
  )

  const setCustomerId = useCallback((nextCustomerId: string) => {
    setCustomerIdState(nextCustomerId)
    localStorage.setItem(STORAGE_KEY, nextCustomerId)
  }, [])

  useEffect(() => {
    if (isLoading || customers.length === 0) {
      return
    }

    const storedIsValid =
      customerId !== null && customers.some((customer) => customer.id === customerId)

    if (!storedIsValid) {
      setCustomerId(customers[0].id)
    }
  }, [customerId, customers, isLoading, setCustomerId])

  const selectedCustomer = useMemo(
    () => customers.find((customer) => customer.id === customerId) ?? null,
    [customers, customerId],
  )

  const value = useMemo(
    () => ({
      customers,
      customerId,
      selectedCustomer,
      setCustomerId,
      isLoading,
    }),
    [customers, customerId, selectedCustomer, setCustomerId, isLoading],
  )

  return (
    <CustomerContext.Provider value={value}>{children}</CustomerContext.Provider>
  )
}

export function useCustomer() {
  const context = useContext(CustomerContext)
  if (!context) {
    throw new Error("useCustomer must be used within a CustomerProvider")
  }
  return context
}
