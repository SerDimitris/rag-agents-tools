import type { CustomerPublic } from "@rag-agent/shared"
import type { ColumnDef } from "@tanstack/react-table"
import { cn } from "@/lib/utils"
import { CustomerActionsMenu } from "./CustomerActionsMenu"

export const columns: ColumnDef<CustomerPublic>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => <span className="font-medium">{row.original.name}</span>,
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {row.original.description || "—"}
      </span>
    ),
  },
  {
    accessorKey: "sector",
    header: "Sector",
    cell: ({ row }) => (
      <span className="text-muted-foreground capitalize">
        {row.original.sector ?? "general"}
      </span>
    ),
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "size-2 rounded-full",
            row.original.is_active ? "bg-green-500" : "bg-gray-400",
          )}
        />
        <span className={row.original.is_active ? "" : "text-muted-foreground"}>
          {row.original.is_active ? "Active" : "Inactive"}
        </span>
      </div>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <CustomerActionsMenu customer={row.original} />
      </div>
    ),
  },
]
