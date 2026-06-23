(function(){const t="rag-agent-chat-widget-root";function d(){const e=document.createElement("style");return e.textContent=`
    #${t} {
      all: initial;
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 2147483647;
      font-family: system-ui, -apple-system, sans-serif;
    }
    #${t} * {
      box-sizing: border-box;
    }
    #${t} .rag-agent-fab {
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
    #${t} .rag-agent-fab:hover {
      background: #1d4ed8;
    }
    #${t} .rag-agent-panel {
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
    #${t} .rag-agent-panel.hidden {
      display: none;
    }
  `,e}function o(){if(document.getElementById(t))return;const e=document.createElement("div");e.id=t;const a=document.createElement("iframe");a.className="rag-agent-panel hidden",a.src=chrome.runtime.getURL("panel.html"),a.title="RAG Chat Assistant";const n=document.createElement("button");n.className="rag-agent-fab",n.type="button",n.setAttribute("aria-label","Open chat assistant"),n.textContent="💬",n.addEventListener("click",()=>{const i=a.classList.contains("hidden");a.classList.toggle("hidden",!i),n.textContent=i?"✕":"💬"}),e.appendChild(d()),e.appendChild(a),e.appendChild(n),document.body.appendChild(e)}document.readyState==="loading"?document.addEventListener("DOMContentLoaded",o):o();
})()
