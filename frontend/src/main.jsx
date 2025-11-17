import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './app.jsx' // Imports your App.jsx
import './index.css'     // Imports your styles

// This finds the "root" div in your index.html and injects your App
ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)