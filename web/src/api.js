/**
 * api.js - The ONLY place that calls the backend server.
 * Every component must call these exported functions; never call fetch directly from components.
 * If the server is unreachable, falls back to loading /sample-result.json from web/public and marks mode as "sample".
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function fetchSampleFallback() {
  try {
    const res = await fetch('/sample-result.json')
    if (!res.ok) {
      throw new Error(`Fallback HTTP error ${res.status}`)
    }
    const data = await res.json()
    return {
      ...data,
      mode: 'sample'
    }
  } catch (err) {
    console.error('Failed to load sample fallback:', err)
    return {
      status: 'complete',
      mode: 'sample',
      _note: 'Fallback placeholder (network offline)',
      area: null,
      dates_used: {},
      files_used: [],
      result_map_url: '',
      area_changed_by_category: {},
      confidence: 0,
      confidence_reason: 'Offline sample fallback',
      limits: 'Sample data placeholder',
      source_type: 'Sample'
    }
  }
}

export async function getAvailability(area) {
  try {
    const res = await fetch(`${API_BASE}/availability`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ area })
    })
    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`)
    }
    return await res.json()
  } catch (err) {
    console.warn('API /availability unreachable, using fallback sample data:', err.message)
    const fallback = await fetchSampleFallback()
    return {
      mode: 'sample',
      passes: [
        {
          granule_id: 'SAMPLE_PASS_01',
          date: '2024-10-01',
          orbit_direction: 'Ascending',
          quality_level: 'nominal'
        },
        {
          granule_id: 'SAMPLE_PASS_02',
          date: '2024-10-15',
          orbit_direction: 'Ascending',
          quality_level: 'nominal'
        }
      ],
      sample_result: fallback
    }
  }
}

export async function startAnalysis(req) {
  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req)
    })
    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`)
    }
    return await res.json()
  } catch (err) {
    console.warn('API /analyze unreachable, returning sample mock job:', err.message)
    return {
      job_id: 'sample-local-job-00000000',
      mode: 'sample'
    }
  }
}

export async function getJob(id) {
  try {
    const res = await fetch(`${API_BASE}/jobs/${id}`)
    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`)
    }
    return await res.json()
  } catch (err) {
    console.warn(`API /jobs/${id} unreachable, returning sample status:`, err.message)
    return {
      job_id: id,
      status: 'complete',
      step: 'Completed mock sample analysis (offline mode)',
      mode: 'sample'
    }
  }
}

export async function getResult(id) {
  try {
    const res = await fetch(`${API_BASE}/results/${id}`)
    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`)
    }
    return await res.json()
  } catch (err) {
    console.warn(`API /results/${id} unreachable, falling back to /sample-result.json:`, err.message)
    return await fetchSampleFallback()
  }
}

