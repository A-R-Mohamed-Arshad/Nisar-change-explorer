import React, { useEffect, useState } from 'react'
import { getJob } from '../api'

/**
 * ProgressDisplay
 * Polls getJob(id) through api.js every 1.5 seconds.
 * Shows the current step message in plain words and an honest "this can take a minute or two" note.
 * Stops automatically on complete or failed.
 * On failed, displays the plain error message from the server.
 */
export default function ProgressDisplay({ jobId, onComplete, onFailed }) {
  const [status, setStatus] = useState('queued')
  const [step, setStep] = useState('Finding passes')
  const [errorMsg, setErrorMsg] = useState(null)

  useEffect(() => {
    if (!jobId) return

    let isMounted = true
    const interval = setInterval(async () => {
      try {
        const job = await getJob(jobId)
        if (!isMounted) return

        setStatus(job.status)
        if (job.step) setStep(job.step)

        if (job.status === 'complete') {
          clearInterval(interval)
          if (onComplete) onComplete(job)
        } else if (job.status === 'failed') {
          clearInterval(interval)
          const message = job.error?.message || 'Processing failed. Please try again with a different area.'
          setErrorMsg(message)
          if (onFailed) onFailed(job.error || { message })
        }
      } catch (err) {
        if (!isMounted) return
        setErrorMsg(err.message || 'Error communicating with analysis service.')
      }
    }, 1500)

    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [jobId, onComplete, onFailed])

  if (!jobId) return null

  return (
    <div
      data-testid="progress-display"
      style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: 8,
        padding: 16,
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        maxWidth: 380,
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#4a5568' }}>Status</span>
        <span
          style={{
            fontSize: 12,
            fontWeight: 700,
            textTransform: 'uppercase',
            color: status === 'complete' ? '#2f855a' : status === 'failed' ? '#c53030' : '#d69e2e'
          }}
        >
          {status}
        </span>
      </div>

      {status !== 'failed' ? (
        <>
          <div style={{ fontSize: 15, fontWeight: 500, color: '#2d3748', marginBottom: 6 }}>
            {step}
          </div>
          <div style={{ fontSize: 12, color: '#718096', fontStyle: 'italic' }}>
            Note: RADAR processing & coregistration can take a minute or two.
          </div>
        </>
      ) : (
        <div
          style={{
            marginTop: 8,
            padding: 10,
            background: '#fff5f5',
            color: '#c53030',
            fontSize: 13,
            borderRadius: 6,
            border: '1px solid #feb2b2'
          }}
        >
          <strong>Error:</strong> {errorMsg}
        </div>
      )}
    </div>
  )
}
