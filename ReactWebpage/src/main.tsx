import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'

// pick a theme (light shown here)
import '@primer/primitives/dist/css/functional/themes/light.css'
import '@primer/primitives/dist/css/primitives.css'

import {ThemeProvider, BaseStyles} from '@primer/react'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <BaseStyles>
        <App />
      </BaseStyles>
    </ThemeProvider>
  </React.StrictMode>
)
