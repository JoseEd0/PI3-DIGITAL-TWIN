import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En desarrollo el tablero corre en 5173 y el servicio en 8000: el proxy deja usar rutas
// relativas (/api/...), igual que cuando el servicio sirve el tablero ya construido.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
