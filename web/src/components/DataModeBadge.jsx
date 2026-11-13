import React from 'react'

/**
 * DataModeBadge
 * Displays LIVE, SAVED or SAMPLE DATA badge based on result's mode.
 * Rule: Never present sample data as live.
 */
export default function DataModeBadge({ mode = 'sample' }) {
  const normalized = (mode || 'sample').toLowerCase()

  let text = 'SAMPLE DATA'
  let bgColor = '#e53e3e' // Red for sample
  let textColor = '#ffffff'

  if (normalized === 'live') {
    text = 'LIVE DATA'
    bgColor = '#38a169' // Green for live
  } else if (normalized === 'saved') {
    text = 'SAVED / CACHED'
    bgColor = '#3182ce' // Blue for saved
  }

  return (
    <span
      data-testid="data-mode-badge"
      style={{
        backgroundColor: bgColor,
        color: textColor,
        fontSize: '11px',
        fontWeight: 700,
        padding: '3px 9px',
        borderRadius: '9999px',
        letterSpacing: '0.5px',
        display: 'inline-flex',
        alignItems: 'center',
        textTransform: 'uppercase',
        boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
      }}
    >
      {text}
    </span>
  )
}
