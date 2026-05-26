export async function send2trash(path: string): Promise<void> {
  try {
    await fetch('/api/v1/system/trash', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path }),
    })
  } catch (e) {
    console.error('send2trash error:', e)
  }
}

export function truncateText(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text
  return text.slice(0, maxLen) + '...'
}
