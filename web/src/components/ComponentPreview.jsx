import React, { useState } from 'react'
import DataModeBadge from './DataModeBadge'
import BeforeAfterSlider from './BeforeAfterSlider'
import ProgressDisplay from './ProgressDisplay'

/**
 * ComponentPreview
 * Demo preview for testing server/pipeline UI components independently without real backend.
 */
export default function ComponentPreview() {
  const [demoMode, setDemoMode] = useState('sample')

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif', maxWidth: 600, background: '#f7fafc', borderRadius: 8 }}>
      <h3 style={{ margin: '0 0 12px 0' }}>Pipeline Component Previews</h3>

      <div style={{ marginBottom: 16 }}>
        <h4>1. DataModeBadge</h4>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <DataModeBadge mode="live" />
          <DataModeBadge mode="saved" />
          <DataModeBadge mode="sample" />
        </div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <h4>2. BeforeAfterSlider</h4>
        <BeforeAfterSlider />
      </div>

      <div style={{ marginBottom: 16 }}>
        <h4>3. ProgressDisplay (Mock Job)</h4>
        <ProgressDisplay jobId="mock-sample-job" />
      </div>
    </div>
  )
}
