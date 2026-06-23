import { useMutation, useQueryClient } from "@tanstack/react-query"
import { CloudUpload, FileText, Plus } from "lucide-react"
import { useCallback, useRef, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { useCustomer } from "@/contexts/CustomerContext"
import { uploadDocument } from "@/lib/uploadDocument"
import { cn } from "@/lib/utils"

const ACCEPTED_TYPES = ".txt,.md,.pdf,.csv,.json"

const UploadDocument = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { customerId, selectedCustomer } = useCustomer()

  const resetForm = () => {
    setTitle("")
    setSelectedFile(null)
    setIsDragging(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const mutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile) {
        throw new Error("Please select a file to upload")
      }
      if (!customerId) {
        throw new Error("Please select a customer first")
      }
      return uploadDocument(selectedFile, customerId, title.trim() || undefined)
    },
    onSuccess: () => {
      showSuccessToast("Document uploaded. Extraction started.")
      resetForm()
      setIsOpen(false)
    },
    onError: (error: Error) => {
      showErrorToast(error.message)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] })
    },
  })

  const handleFileSelection = (file: File | null) => {
    if (!file) return
    setSelectedFile(file)
    if (!title.trim()) {
      setTitle(file.name.replace(/\.[^.]+$/, ""))
    }
  }

  const onDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    const file = event.dataTransfer.files?.[0]
    handleFileSelection(file ?? null)
  }, [title])

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        setIsOpen(open)
        if (!open) resetForm()
      }}
    >
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Upload Document
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>
            Upload to{" "}
            <strong>{selectedCustomer?.name ?? "selected customer"}</strong>.
            Drag and drop a file here or browse your computer. Supported
            formats: TXT, MD, PDF, CSV, JSON.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-2">
          <div className="grid gap-2">
            <Label htmlFor="document-title">Title (optional)</Label>
            <Input
              id="document-title"
              placeholder="Document title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </div>

          <div
            role="button"
            tabIndex={0}
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                fileInputRef.current?.click()
              }
            }}
            onDragOver={(event) => {
              event.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            className={cn(
              "flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed p-6 text-center transition-colors",
              isDragging
                ? "border-primary bg-primary/5"
                : "border-muted-foreground/30 hover:border-primary/50",
            )}
          >
            {selectedFile ? (
              <>
                <FileText className="mb-2 h-8 w-8 text-primary" />
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </>
            ) : (
              <>
                <CloudUpload className="mb-2 h-8 w-8 text-muted-foreground" />
                <p className="font-medium">Drop your file here</p>
                <p className="text-sm text-muted-foreground">
                  or click to open your file explorer
                </p>
              </>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED_TYPES}
            className="hidden"
            onChange={(event) =>
              handleFileSelection(event.target.files?.[0] ?? null)
            }
          />
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>
              Cancel
            </Button>
          </DialogClose>
          <LoadingButton
            loading={mutation.isPending}
            disabled={!selectedFile || !customerId}
            onClick={() => mutation.mutate()}
          >
            Upload
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default UploadDocument
