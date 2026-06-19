import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { DocumentsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddDocument from "@/components/Documents/AddDocument"
import { getDocumentColumns } from "@/components/Documents/columns"
import PendingDocuments from "@/components/Pending/PendingDocuments"
import useAuth from "@/hooks/useAuth"
import { canManageDocuments } from "@/lib/roles"

function getDocumentsQueryOptions() {
  return {
    queryFn: () => DocumentsService.readDocuments({ skip: 0, limit: 100 }),
    queryKey: ["documents"],
  }
}

export const Route = createFileRoute("/_layout/documents")({
  component: Documents,
  head: () => ({
    meta: [
      {
        title: "Documents - FastAPI Template",
      },
    ],
  }),
})

function DocumentsTableContent() {
  const { user } = useAuth()
  const canManage = canManageDocuments(user)
  const { data: documents } = useSuspenseQuery(getDocumentsQueryOptions())

  if (documents.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No documents yet</h3>
        <p className="text-muted-foreground">
          {canManage
            ? "Add a new document to get started"
            : "Documents will appear here once they are uploaded"}
        </p>
      </div>
    )
  }

  return (
    <DataTable
      columns={getDocumentColumns(canManage)}
      data={documents.data}
    />
  )
}

function DocumentsTable() {
  return (
    <Suspense fallback={<PendingDocuments />}>
      <DocumentsTableContent />
    </Suspense>
  )
}

function Documents() {
  const { user } = useAuth()
  const canManage = canManageDocuments(user)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground">
            View and manage uploaded documents
          </p>
        </div>
        {canManage && <AddDocument />}
      </div>
      <DocumentsTable />
    </div>
  )
}
