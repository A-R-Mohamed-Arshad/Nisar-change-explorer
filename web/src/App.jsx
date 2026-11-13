import React, { useEffect, useRef, useState } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { GIBS_CONFIG, getGibsTileUrl } from './config'
import { getAvailability } from './api'

export default function App() {
  const mapContainer = useRef(null)
  const map = useRef(null)
  const [dataMode, setDataMode] = useState('sample')
  const [gibsEnabled, setGibsEnabled] = useState(GIBS_CONFIG.defaultEnabled)

  useEffect(() => {
    // Initial test call to API to establish status/mode
    getAvailability({ type: 'Point', coordinates: [80.0, 12.0] })
      .then((data) => {
        if (data?.mode) {
          setDataMode(data.mode)
        }
      })
      .catch(() => {
        setDataMode('sample')
      })
  }, [])

  useEffect(() => {
    if (map.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm-basemap': {
            type: 'raster',
            tiles: [
              'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          },
          'nasa-gibs-nisar': {
            type: 'raster',
            tiles: [
              getGibsTileUrl()
            ],
            tileSize: 256,
            attribution: 'Imagery &copy; NASA EOSDIS GIBS'
          }
        },
        layers: [
          {
            id: 'osm-layer',
            type: 'raster',
            source: 'osm-basemap',
            minzoom: 0,
            maxzoom: 19
          },
          {
            id: 'gibs-nisar-layer',
            type: 'raster',
            source: 'nasa-gibs-nisar',
            layout: {
              visibility: GIBS_CONFIG.defaultEnabled ? 'visible' : 'none'
            },
            paint: {
              'raster-opacity': 0.75
            }
          }
        ]
      },
      center: [79.8, 12.0], // Default center around sample coordinates
      zoom: 6
    })

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right')

    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [])

  const toggleGibsLayer = () => {
    if (!map.current) return
    const nextState = !gibsEnabled
    setGibsEnabled(nextState)
    if (map.current.getLayer('gibs-nisar-layer')) {
      map.current.setLayoutProperty(
        'gibs-nisar-layer',
        'visibility',
        nextState ? 'visible' : 'none'
      )
    }
  }

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', margin: 0, padding: 0, overflow: 'hidden' }}>
      {/* Map container */}
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />

      {/* Header and Controls Overlay */}
      <div style={{
        position: 'absolute',
        top: 16,
        left: 16,
        zIndex: 10,
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '12px 18px',
        borderRadius: 8,
        boxShadow: '0 2px 10px rgba(0,0,0,0.15)',
        fontFamily: 'sans-serif'
      }}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          NISAR Change Explorer
          {dataMode === 'sample' && (
            <span style={{
              backgroundColor: '#e53e3e',
              color: '#ffffff',
              fontSize: '11px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '9999px',
              letterSpacing: '0.5px'
            }}>
              SAMPLE DATA
            </span>
          )}
        </h2>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', gap: '6px' }}>
            <input
              type="checkbox"
              checked={gibsEnabled}
              onChange={toggleGibsLayer}
            />
            NASA GIBS NISAR Layer (Raster Overlay)
          </label>
        </div>
        {gibsEnabled && (
          <div style={{ fontSize: '11px', color: '#666', marginTop: '4px' }}>
            Layer ID: {GIBS_CONFIG.layerId} (Draft / TODO)
          </div>
        )}
      </div>
    </div>
  )
}

