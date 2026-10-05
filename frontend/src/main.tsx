import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { Toaster } from 'react-hot-toast'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
    <Toaster 
      position="top-right" 
      toastOptions={{
        className: '!bg-surface-800 !text-surface-100 !border !border-surface-700 !shadow-lg',
      }}
    />
  </React.StrictMode>,
)
