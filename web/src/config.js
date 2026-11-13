/**
 * Global configuration for NASA GIBS and NISAR raster layers.
 *
 * NOTE: The exact NASA GIBS layer ID for NISAR will be confirmed once operational
 * products are publicly broadcast on GIBS WMTS/TMS endpoints.
 * DO NOT invent a fake layer ID; keep this clearly marked as TODO.
 */

export const GIBS_CONFIG = {
  // TODO: Replace with the official GIBS NISAR layer identifier once confirmed by NASA
  layerId: 'TODO_CONFIRM_GIBS_NISAR_LAYER_ID',
  date: '2024-10-01',
  tileMatrixSet: 'GoogleMapsCompatible_Level8',
  format: 'png',
  // Standard NASA GIBS WMTS / EPSG:3857 template
  // https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layer}/default/{date}/{tileMatrixSet}/{z}/{y}/{x}.{format}
  wmtsTemplate: 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layerId}/default/{date}/{tileMatrixSet}/{z}/{y}/{x}.{format}',
  defaultEnabled: false // Load fine with the layer off initially
}

export function getGibsTileUrl() {
  return GIBS_CONFIG.wmtsTemplate
    .replace('{layerId}', GIBS_CONFIG.layerId)
    .replace('{date}', GIBS_CONFIG.date)
    .replace('{tileMatrixSet}', GIBS_CONFIG.tileMatrixSet)
    .replace('{format}', GIBS_CONFIG.format)
}

