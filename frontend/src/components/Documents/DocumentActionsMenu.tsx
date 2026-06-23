import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { DocumentPublic } from "@rag-agent/shared"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteDocument from "./DeleteDocument"
import EditDocument from "./EditDocument"

interface DocumentActionsMenuProps {
  document: DocumentPublic
}

export const DocumentActionsMenu = ({ document }: DocumentActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditDocument document={document} onSuccess={() => setOpen(false)} />
        <DeleteDocument
          id={document.id}
          customerId={document.customer_id}
          onSuccess={() => setOpen(false)}
        />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
