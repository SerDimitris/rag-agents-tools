import { useQuery } from "@tanstack/react-query"
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react"

import { getStorageAdapter } from "../api/configure-api"
import { CustomersService, type CustomerPublic } from "../client"
import { SELECTED_CUSTOMER_KEY } from "../storage/types"

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

export function CustomerProvider({
  children,
  enabled = true,
}: {
  children: React.ReactNode
  enabled?: boolean
}) {
  const storage = getStorageAdapter()
  const { data, isLoading: customersLoading } = useQuery({
    ...getCustomersQueryOptions(),
    enabled,
  })
  const customers = data?.data ?? []

  const [customerId, setCustomerIdState] = useState<string | null>(null)
  const [storageReady, setStorageReady] = useState(false)

  useEffect(() => {
    void (async () => {
      const stored = await storage.getItem(SELECTED_CUSTOMER_KEY)
      setCustomerIdState(stored)
      setStorageReady(true)
    })()
  }, [storage])

  const setCustomerId = useCallback(
    (nextCustomerId: string) => {
      setCustomerIdState(nextCustomerId)
      void storage.setItem(SELECTED_CUSTOMER_KEY, nextCustomerId)
    },
    [storage],
  )

  useEffect(() => {
    if (!storageReady || customersLoading || customers.length === 0) {
      return
    }

    const storedIsValid =
      customerId !== null && customers.some((customer) => customer.id === customerId)

    if (!storedIsValid) {
      setCustomerId(customers[0].id)
    }
  }, [customerId, customers, customersLoading, setCustomerId, storageReady])

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
      isLoading: customersLoading || !storageReady,
    }),
    [customers, customerId, selectedCustomer, setCustomerId, customersLoading, storageReady],
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
