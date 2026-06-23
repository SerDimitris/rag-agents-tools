const ROOT_ID = "rag-agent-chat-widget-root"

function createStyles(): HTMLStyleElement {
  const style = document.createElement("style")
  style.textContent = `
    #${ROOT_ID} {
      all: initial;
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 2147483647;
      font-family: system-ui, -apple-system, sans-serif;
    }
    #${ROOT_ID} * {
      box-sizing: border-box;
    }
    #${ROOT_ID} .rag-agent-fab {
      all: unset;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: #2563eb;
      color: #fff;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
      font-size: 24px;
      line-height: 1;
    }
    #${ROOT_ID} .rag-agent-fab:hover {
      background: #1d4ed8;
    }
    #${ROOT_ID} .rag-agent-panel {
      position: absolute;
      bottom: 68px;
      right: 0;
      width: 380px;
      height: 520px;
      border: none;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
      background: #fff;
    }
    #${ROOT_ID} .rag-agent-panel.hidden {
      display: none;
    }
  `
  return style
}

function initWidget(): void {
  if (document.getElementById(ROOT_ID)) {
    return
  }

  const root = document.createElement("div")
  root.id = ROOT_ID

  const panel = document.createElement("iframe")
  panel.className = "rag-agent-panel hidden"
  panel.src = chrome.runtime.getURL("panel.html")
  panel.title = "RAG Chat Assistant"

  const fab = document.createElement("button")
  fab.className = "rag-agent-fab"
  fab.type = "button"
  fab.setAttribute("aria-label", "Open chat assistant")
  fab.textContent = "💬"

  fab.addEventListener("click", () => {
    const isHidden = panel.classList.contains("hidden")
    panel.classList.toggle("hidden", !isHidden)
    fab.textContent = isHidden ? "✕" : "💬"
  })

  root.appendChild(createStyles())
  root.appendChild(panel)
  root.appendChild(fab)
  document.body.appendChild(root)
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initWidget)
} else {
  initWidget()
}
