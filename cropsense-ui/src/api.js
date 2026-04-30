const BASE = '/api'

async function req(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || res.statusText)
  }
  return res.json()
}

export const api = {
  health:            ()       => req('GET',  '/health'),
  stats:             ()       => req('GET',  '/stats'),
  crops:             ()       => req('GET',  '/crops'),
  featureImportance: ()       => req('GET',  '/feature-importance'),
  predict:           (data)   => req('POST', '/predict', data),
  optimize:          (data)   => req('POST', '/optimize-crop', data),
  batchPredict:      (rows)   => req('POST', '/batch-predict', rows),
}
