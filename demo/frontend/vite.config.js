import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En desarrollo el tablero corre en 5173 y el servidor del gemelo en 8000; el
// proxy deja que el codigo use siempre rutas relativas (/api/...), igual que
// cuando la Raspberry Pi sirve el tablero ya construido.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
