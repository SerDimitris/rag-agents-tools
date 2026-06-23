import { useCustomer } from "../contexts/CustomerContext"

type CustomerSelectProps = {
  className?: string
  selectClassName?: string
  labelClassName?: string
  showLabel?: boolean
}

export function CustomerSelect({
  className,
  selectClassName,
  labelClassName,
  showLabel = true,
}: CustomerSelectProps) {
  const { customers, customerId, setCustomerId, isLoading } = useCustomer()

  if (isLoading) {
    return (
      <span className={labelClassName ?? "text-sm text-muted-foreground"}>
        Loading customers...
      </span>
    )
  }

  if (customers.length === 0) {
    return (
      <span className={labelClassName ?? "text-sm text-muted-foreground"}>
        No customers available
      </span>
    )
  }

  return (
    <div className={className ?? "flex items-center gap-2"}>
      {showLabel && (
        <span className={labelClassName ?? "text-sm font-medium text-muted-foreground"}>
          Customer
        </span>
      )}
      <select
        className={selectClassName ?? "rounded border px-2 py-1 text-sm"}
        value={customerId ?? ""}
        onChange={(event) => setCustomerId(event.target.value)}
      >
        {!customerId && <option value="">Select customer</option>}
        {customers.map((customer) => (
          <option key={customer.id} value={customer.id}>
            {customer.name}
          </option>
        ))}
      </select>
    </div>
  )
}
