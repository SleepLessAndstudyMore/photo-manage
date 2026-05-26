import client from './client'

export function getSystemStatus() {
  return client.get('/system/status')
}

export function getSystemConfig() {
  return client.get('/system/config')
}

export function updateSystemConfig(data: Record<string, unknown>) {
  return client.put('/system/config', data)
}

export function getTasks() {
  return client.get('/tasks')
}

export function getTask(id: number) {
  return client.get(`/tasks/${id}`)
}

export function cancelTask(id: number) {
  return client.post(`/tasks/${id}/cancel`)
}
