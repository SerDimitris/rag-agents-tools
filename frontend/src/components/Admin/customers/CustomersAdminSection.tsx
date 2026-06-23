import { useSuspenseQuery } from "@tanstack/react-query"
import { Suspense } from "react"

import { CustomersService } from "@/client"
import AddCustomer from "@/components/Admin/customers/AddCustomer"
import { columns } from "@/components/Admin/customers/columns"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers"

function getAdminCustomersQueryOptions() {
  return {
    queryFn: () =>
      CustomersService.readCustomers({
        skip: 0,
        limit: 100,
        includeInactive: true,
      }),
    queryKey: ["admin-customers"],
  }
}

function CustomersTableContent() {
  const { data: customers } = useSuspenseQuery(getAdminCustomersQueryOptions())
  return <DataTable columns={columns} data={customers.data} />
}

export function CustomersAdminSection() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Customers</h2>
          <p className="text-muted-foreground">
            Manage customer projects and their isolated knowledge bases
          </p>
        </div>
        <AddCustomer />
      </div>
      <Suspense fallback={<PendingUsers />}>
        <CustomersTableContent />
      </Suspense>
    </div>
  )
}
