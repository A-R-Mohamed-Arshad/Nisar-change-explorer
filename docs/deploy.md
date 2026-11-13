# Deployment Guide: NISAR Change Explorer

This guide covers deployment options for the NISAR Change Explorer web application and FastAPI server, including pre-flight verification, environment setup, and public exposure.

---

## 1. Pre-Flight Checklist

Before deploying, ensure:
- [ ] No API keys, NASA passwords, or local `.env` files are committed in Git.
- [ ] Automated tests pass: `pytest server/tests`.
- [ ] Web production build succeeds: `cd web && npm run build`.
- [ ] `VITE_API_BASE` points to the publicly accessible server URL.
- [ ] Server's `ALLOWED_ORIGINS` includes the production domain of the web application.
- [ ] `CACHE_DIR` is mounted on persistent storage or writable disk.

---

## 2. Deploying the Web App (Vercel)

We use Vercel via the root `vercel.json` configuration:

1. **Connect GitHub Repo**: In the Vercel dashboard, import `Nisar-change-explorer`.
2. **Configure Build Settings**:
   - Framework Preset: `Vite`
   - Root Directory: `./` (or `web/`)
   - Build Command: `cd web && npm run build` (handled automatically by `vercel.json`)
   - Output Directory: `web/dist`
3. **Environment Variables**:
   - `VITE_API_BASE`: Set to the deployed backend URL (e.g., `https://api.nisar-change-explorer.com` or your cloud VM URL).
4. **Deploy**: Trigger deployment. Single Page Application (SPA) client-side routes will rewrite to `/index.html`.

---

## 3. Running the Server on a Cloud VM with Docker

### 3.1 Build Docker Image
From the repository root:
```bash
docker build -t nisar-server -f server/Dockerfile .
```

### 3.2 Run Docker Container
```bash
docker run -d \
  --name nisar-backend \
  -p 8000:8000 \
  -v $(pwd)/cache:/app/cache \
  -e ALLOWED_ORIGINS="https://your-web-app.vercel.app,http://localhost:5173" \
  -e EARTHDATA_USERNAME="your-earthdata-username" \
  -e EARTHDATA_PASSWORD="your-earthdata-password" \
  -e MAX_AREA_KM="25" \
  nisar-server
```

Verify health check:
```bash
curl http://<VM_PUBLIC_IP>:8000/health
# Expected: {"ok": true}
```

---

## 4. Exposing a Laptop-Run Server via Tunnel

During hackathon demos, you can run the FastAPI server locally on your laptop and expose it over HTTPS using either Cloudflare Tunnels (`cloudflared`) or `ngrok`.

### Option A: Cloudflare Tunnels (Recommended, No Timeouts)
1. Start your server locally:
   ```cmd
   cd server
   .venv\Scripts\activate
   uvicorn main:app --port 8000
   ```
2. In a separate terminal, launch `cloudflared`:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
3. Copy the generated `https://*.trycloudflare.com` URL.
4. Set in `web/.env`:
   ```env
   VITE_API_BASE=https://random-subdomain.trycloudflare.com
   ```
5. Update server `ALLOWED_ORIGINS` to allow traffic from your web dev or preview domain.

### Option B: ngrok
1. Run ngrok on port 8000:
   ```bash
   ngrok http 8000
   ```
2. Copy the forwarded HTTPS URL (e.g. `https://abc-123.ngrok-free.app`).
3. Set `VITE_API_BASE=https://abc-123.ngrok-free.app` on the web client.
4. Ensure `ALLOWED_ORIGINS` on the server includes the client origin.
