import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { CustomerPublic } from "@rag-agent/shared"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteCustomer from "./DeleteCustomer"
import EditCustomer from "./EditCustomer"

interface CustomerActionsMenuProps {
  customer: CustomerPublic
}

export const CustomerActionsMenu = ({ customer }: CustomerActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditCustomer customer={customer} onSuccess={() => setOpen(false)} />
        <DeleteCustomer id={customer.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
