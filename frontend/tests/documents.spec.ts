import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import {
  randomDocumentFilePath,
  randomDocumentTitle,
  randomEmail,
  randomPassword,
} from "./utils/random"
import { logInUser } from "./utils/user"

test("Documents page is accessible and shows correct title", async ({
  page,
}) => {
  await page.goto("/documents")
  await expect(page.getByRole("heading", { name: "Documents" })).toBeVisible()
  await expect(
    page.getByText("View and manage uploaded documents"),
  ).toBeVisible()
})

test("Add Document button is visible for superuser", async ({ page }) => {
  await page.goto("/documents")
  await expect(
    page.getByRole("button", { name: "Add Document" }),
  ).toBeVisible()
})

test.describe("Documents management", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/documents")
  })

  test("Create a new document successfully", async ({ page }) => {
    const title = randomDocumentTitle()
    const filePath = randomDocumentFilePath()

    await page.getByRole("button", { name: "Add Document" }).click()
    await page.getByLabel("Title").fill(title)
    await page.getByLabel("File Path").fill(filePath)
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("Document created successfully")).toBeVisible()
    await expect(page.getByText(title)).toBeVisible()
  })

  test("Create document with only required fields", async ({ page }) => {
    const title = randomDocumentTitle()
    const filePath = randomDocumentFilePath()

    await page.getByRole("button", { name: "Add Document" }).click()
    await page.getByLabel("Title").fill(title)
    await page.getByLabel("File Path").fill(filePath)
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("Document created successfully")).toBeVisible()
    await expect(page.getByText(title)).toBeVisible()
  })

  test("Cancel document creation", async ({ page }) => {
    await page.getByRole("button", { name: "Add Document" }).click()
    await page.getByLabel("Title").fill("Test Document")
    await page.getByRole("button", { name: "Cancel" }).click()

    await expect(page.getByRole("dialog")).not.toBeVisible()
  })

  test("Title is required", async ({ page }) => {
    await page.getByRole("button", { name: "Add Document" }).click()
    await page.getByLabel("Title").fill("")
    await page.getByLabel("Title").blur()

    await expect(page.getByText("Title is required")).toBeVisible()
  })

  test.describe("Edit and Delete", () => {
    let documentTitle: string

    test.beforeEach(async ({ page }) => {
      documentTitle = randomDocumentTitle()

      await page.getByRole("button", { name: "Add Document" }).click()
      await page.getByLabel("Title").fill(documentTitle)
      await page.getByLabel("File Path").fill(randomDocumentFilePath())
      await page.getByRole("button", { name: "Save" }).click()
      await expect(
        page.getByText("Document created successfully"),
      ).toBeVisible()
      await expect(page.getByRole("dialog")).not.toBeVisible()
    })

    test("Edit a document successfully", async ({ page }) => {
      const documentRow = page
        .getByRole("row")
        .filter({ hasText: documentTitle })
      await documentRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Edit Document" }).click()

      const updatedTitle = randomDocumentTitle()
      await page.getByLabel("Title").fill(updatedTitle)
      await page.getByRole("button", { name: "Save" }).click()

      await expect(page.getByText("Document updated successfully")).toBeVisible()
      await expect(page.getByText(updatedTitle)).toBeVisible()
    })

    test("Delete a document successfully", async ({ page }) => {
      const documentRow = page
        .getByRole("row")
        .filter({ hasText: documentTitle })
      await documentRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Delete Document" }).click()

      await page.getByRole("button", { name: "Delete" }).click()

      await expect(
        page.getByText("The document was deleted successfully"),
      ).toBeVisible()
      await expect(page.getByText(documentTitle)).not.toBeVisible()
    })
  })
})

test.describe("Documents viewer access", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("Viewer cannot see Add Document button", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/documents")

    await expect(
      page.getByRole("button", { name: "Add Document" }),
    ).not.toBeVisible()
  })
})
