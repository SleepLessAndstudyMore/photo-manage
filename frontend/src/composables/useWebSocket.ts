import { ref, onUnmounted } from 'vue'

export interface WsMessage {
  type: string
  data: {
    task_id: string
    library_id: number | null
    progress: number
    message: string
    status?: string
  }
}

export function useWebSocket() {
  const isConnected = ref(false)
  const lastMessage = ref<WsMessage | null>(null)
  const listeners = new Set<(msg: WsMessage) => void>()
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let _manualClose = false

  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return
    }
    _manualClose = false
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${location.host}/api/v1/ws/notifications`
    ws = new WebSocket(url)

    ws.onopen = () => {
      isConnected.value = true
    }

    ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data)
        lastMessage.value = msg
        listeners.forEach((fn) => {
          try { fn(msg) } catch { /* ignore */ }
        })
      } catch { /* ignore malformed JSON */ }
    }

    ws.onclose = () => {
      isConnected.value = false
      if (!_manualClose) {
        reconnectTimer = setTimeout(connect, 3000)
      }
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function onMessage(callback: (msg: WsMessage) => void) {
    listeners.add(callback)
    return () => { listeners.delete(callback) }
  }

  function disconnect() {
    _manualClose = true
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
    listeners.clear()
  }

  onUnmounted(disconnect)

  return { isConnected, lastMessage, connect, disconnect, onMessage }
}
