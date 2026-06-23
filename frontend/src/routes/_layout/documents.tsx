import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { DocumentsService, UsersService } from "@rag-agent/shared"
import { DataTable } from "@/components/Common/DataTable"
import { getDocumentColumns } from "@/components/Documents/columns"
import UploadDocument from "@/components/Documents/UploadDocument"
import PendingDocuments from "@/components/Pending/PendingDocuments"
import { useCustomer } from "@rag-agent/shared"
import useAuth from "@/hooks/useAuth"
import { canAccessDocuments, canManageDocuments } from "@/lib/roles"
import { pageTitle } from "@/lib/brand"

function getDocumentsQueryOptions(customerId: string) {
  return {
    queryFn: () =>
      DocumentsService.readDocuments({
        customerId,
        skip: 0,
        limit: 100,
      }),
    queryKey: ["documents", customerId],
    refetchInterval: 5000,
  }
}

export const Route = createFileRoute("/_layout/documents")({
  component: Documents,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!canAccessDocuments(user)) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: pageTitle("Documents"),
      },
    ],
  }),
})

function DocumentsTableContent() {
  const { user } = useAuth()
  const { customerId, selectedCustomer } = useCustomer()
  const canManage = canManageDocuments(user)

  if (!customerId) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-muted-foreground">Select a customer to view documents.</p>
      </div>
    )
  }

  const { data: documents } = useSuspenseQuery(getDocumentsQueryOptions(customerId))

  if (documents.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No documents yet</h3>
        <p className="text-muted-foreground">
          Upload a document for {selectedCustomer?.name ?? "this customer"} to start
          extraction
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
  const { customerId } = useCustomer()

  if (!customerId) {
    return null
  }

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
            Upload files and track extraction status for the selected customer
          </p>
        </div>
        {canManage && <UploadDocument />}
      </div>
      <DocumentsTable />
    </div>
  )
}
