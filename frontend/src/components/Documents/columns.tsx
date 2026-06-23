import type { ColumnDef } from "@tanstack/react-table"
import { Check, Copy } from "lucide-react"

import type { DocumentPublic } from "@rag-agent/shared"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import { cn } from "@/lib/utils"
import { DocumentActionsMenu } from "./DocumentActionsMenu"

function CopyId({ id }: { id: string }) {
  const [copiedText, copy] = useCopyToClipboard()
  const isCopied = copiedText === id

  return (
    <div className="flex items-center gap-1.5 group">
      <span className="font-mono text-xs text-muted-foreground">{id}</span>
      <Button
        variant="ghost"
        size="icon"
        className="size-6 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={() => copy(id)}
      >
        {isCopied ? (
          <Check className="size-3 text-green-500" />
        ) : (
          <Copy className="size-3" />
        )}
        <span className="sr-only">Copy ID</span>
      </Button>
    </div>
  )
}

function StatusBadge({ status }: { status: DocumentPublic["status"] }) {
  const variant =
    status === "completed"
      ? "default"
      : status === "failed"
        ? "destructive"
        : status === "processing"
          ? "outline"
          : "secondary"

  return (
    <Badge variant={variant}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  )
}

const baseColumns: ColumnDef<DocumentPublic>[] = [
  {
    accessorKey: "id",
    header: "ID",
    cell: ({ row }) => <CopyId id={row.original.id} />,
  },
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.title}</span>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => <StatusBadge status={row.original.status} />,
  },
  {
    accessorKey: "file_path",
    header: "File Path",
    cell: ({ row }) => (
      <span
        className={cn(
          "max-w-xs truncate block text-muted-foreground font-mono text-xs",
        )}
      >
        {row.original.file_path}
      </span>
    ),
  },
]

const actionsColumn: ColumnDef<DocumentPublic> = {
  id: "actions",
  header: () => <span className="sr-only">Actions</span>,
  cell: ({ row }) => (
    <div className="flex justify-end">
      <DocumentActionsMenu document={row.original} />
    </div>
  ),
}

export function getDocumentColumns(
  canManage: boolean,
): ColumnDef<DocumentPublic>[] {
  return canManage ? [...baseColumns, actionsColumn] : baseColumns
}
