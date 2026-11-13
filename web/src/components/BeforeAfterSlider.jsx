import React, { useState } from 'react'

/**
 * BeforeAfterSlider
 * Takes two image URLs (before and after) and provides a swipe slider without extra libraries.
 */
export default function BeforeAfterSlider({
  beforeUrl = 'https://via.placeholder.com/600x400/2b6cb0/ffffff?text=Pre-Event+Radar+(Before)',
  afterUrl = 'https://via.placeholder.com/600x400/c53030/ffffff?text=Post-Event+Radar+(After)',
  width = 400,
  height = 260
}) {
  const [sliderPos, setSliderPos] = useState(50)

  return (
    <div
      data-testid="before-after-slider"
      style={{
        position: 'relative',
        width: `${width}px`,
        maxWidth: '100%',
        height: `${height}px`,
        overflow: 'hidden',
        borderRadius: 8,
        border: '1px solid #cbd5e0',
        userSelect: 'none',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}
    >
      {/* Background (After image) */}
      <img
        src={afterUrl}
        alt="Post-event"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: 8,
          right: 8,
          background: 'rgba(0,0,0,0.7)',
          color: '#fff',
          fontSize: 10,
          padding: '2px 6px',
          borderRadius: 4
        }}
      >
        After (Post)
      </div>

      {/* Foreground (Before image clipped) */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: `${sliderPos}%`,
          height: '100%',
          overflow: 'hidden'
        }}
      >
        <img
          src={beforeUrl}
          alt="Pre-event"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: `${width}px`,
            maxWidth: 'none',
            height: `${height}px`,
            objectFit: 'cover'
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: 8,
            left: 8,
            background: 'rgba(0,0,0,0.7)',
            color: '#fff',
            fontSize: 10,
            padding: '2px 6px',
            borderRadius: 4
          }}
        >
          Before (Pre)
        </div>
      </div>

      {/* Divider line and handle */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: `${sliderPos}%`,
          width: 2,
          background: '#ffffff',
          boxShadow: '0 0 4px rgba(0,0,0,0.5)',
          cursor: 'ew-resize',
          zIndex: 5
        }}
      />

      {/* Hidden range input over full width to enable smooth swiping */}
      <input
        type="range"
        min="0"
        max="100"
        value={sliderPos}
        onChange={(e) => setSliderPos(Number(e.target.value))}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          opacity: 0,
          cursor: 'ew-resize',
          margin: 0,
          zIndex: 10
        }}
        aria-label="Swipe to compare before and after radar views"
      />
    </div>
  )
}
