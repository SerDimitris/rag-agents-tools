import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useCustomer } from "@rag-agent/shared"

export function CustomerSelect() {
  const { customers, customerId, setCustomerId, isLoading } = useCustomer()

  if (isLoading) {
    return (
      <span className="text-sm text-muted-foreground">Loading customers...</span>
    )
  }

  if (customers.length === 0) {
    return (
      <span className="text-sm text-muted-foreground">No customers available</span>
    )
  }

  return (
    <div className="ml-auto flex items-center gap-2">
      <span className="text-sm font-medium text-muted-foreground">Customer</span>
      <Select value={customerId ?? undefined} onValueChange={setCustomerId}>
        <SelectTrigger className="w-[220px]">
          <SelectValue placeholder="Select customer" />
        </SelectTrigger>
        <SelectContent>
          {customers.map((customer) => (
            <SelectItem key={customer.id} value={customer.id}>
              {customer.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
