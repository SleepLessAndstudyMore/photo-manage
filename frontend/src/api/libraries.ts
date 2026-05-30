import client from './client'

export function getLibraries() {
  return client.get('/libraries')
}

export function addLibrary(data: { name: string; path: string }) {
  return client.post('/libraries', data)
}

export function browseDirectory(path?: string) {
  return client.get('/libraries/browse', { params: { path } })
}

export function deleteLibrary(id: number) {
  return client.delete(`/libraries/${id}`)
}

export function scanLibrary(id: number) {
  return client.post(`/libraries/${id}/scan`)
}

export function checkConsistency(id: number) {
  return client.post(`/libraries/${id}/check-consistency`)
}
