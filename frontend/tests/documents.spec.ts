import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import {
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
    page.getByText(
      "Upload files and track extraction status for the selected customer",
    ),
  ).toBeVisible()
})

test("Upload Document button is visible", async ({ page }) => {
  await page.goto("/documents")
  await expect(
    page.getByRole("button", { name: "Upload Document" }),
  ).toBeVisible()
})

test.describe("Documents upload", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/documents")
  })

  test("Upload a document via file picker", async ({ page }) => {
    await page.getByRole("button", { name: "Upload Document" }).click()
    await page.getByLabel("Title (optional)").fill(randomDocumentTitle())
    await page.locator('input[type="file"]').setInputFiles({
      name: "sample.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("Sample uploaded document content."),
    })
    await page.getByRole("button", { name: "Upload" }).click()

    await expect(
      page.getByText("Document uploaded. Extraction started."),
    ).toBeVisible()
  })
})

test.describe("Chat page", () => {
  test("Chat tab is accessible", async ({ page }) => {
    await page.goto("/chat")
    await expect(page.getByRole("heading", { name: "Chat" })).toBeVisible()
    await expect(
      page.getByPlaceholder(/Ask a question about .+'s documents\.\.\./),
    ).toBeVisible()
  })

  test("User can send a chat message", async ({ page }) => {
    await page.goto("/chat")
    await page
      .getByPlaceholder(/Ask a question about .+'s documents\.\.\./)
      .fill("What documents are available?")
    await page.getByRole("button", { name: "Send" }).click()
    await expect(page.getByText("What documents are available?")).toBeVisible()
  })
})

test.describe("Documents viewer access", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("Viewer cannot access documents page", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/documents")
    await expect(page).not.toHaveURL(/\/documents/)
    await expect(
      page.getByRole("heading", { name: "Documents" }),
    ).not.toBeVisible()
  })

  test("Viewer does not see Documents in sidebar", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/")
    await expect(
      page.getByRole("link", { name: "Documents" }),
    ).not.toBeVisible()
    await expect(page.getByRole("link", { name: "Dashboard" })).toBeVisible()
    await expect(page.getByRole("link", { name: "Chat" })).toBeVisible()
  })

  test("Viewer can switch customer in chat", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/chat")
    await expect(page.getByRole("combobox")).toBeVisible()
    await expect(page.getByText("Customer", { exact: true })).toBeVisible()
  })
})
