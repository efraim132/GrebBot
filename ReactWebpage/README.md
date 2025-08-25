# Admin Webpage (React + TypeScript + Vite)

This is the admin UI for the GrebBot project. It’s a TypeScript React app built with Vite, styled with GitHub’s Primer components, and served by the bot’s Flask web server.

- Tech: React + TypeScript + Vite
- UI: Primer React + Primer Primitives
- Backend host: Flask (see web_interface.py at the repo root)
- Output target: templates/ (consumed by Flask)

## How it’s wired
- Build output: vite.config.ts sets `build.outDir = '../templates'`.
  - Vite writes `index.html` to `../templates/index.html` and assets to `../templates/assets/`.
- Flask serving:
  - web_interface.py creates the app with `static_folder='templates/assets'` and serves `/` via `render_template('index.html')`.
  - After a production build, the Flask server at http://127.0.0.1:5000 will serve the built admin UI.

## Quick start
1) Install Node 18+ and npm.
2) Install dependencies:
   - cd ReactWebpage
   - npm install
3) Dev mode (Vite server):
   - npm run dev
   - Open http://localhost:5173
4) Build for Flask (normal build):
   - npm run build
   - Output goes to `../templates` as configured; start the bot and visit http://127.0.0.1:5000
5) Optional preview (static):
   - npm run preview

Notes
- Don’t change `outDir` unless you also update Flask’s template/static config.
- If you see old assets, remove the `templates/` folder and rebuild.

## Primer UI guidelines
Primer is already set up for a clean, accessible UI:
- `@primer/react` components are used throughout. Keep layout simple: PageLayout, Box, Button, ActionMenu, etc.
- `main.tsx` includes `ThemeProvider` and `BaseStyles`, and imports Primer Primitives CSS for consistent tokens.
- Prefer Primer components over custom CSS for spacing, typography, and color to keep the interface clean and consistent.

Useful bits already in place
- ThemeProvider + BaseStyles wrapper
- Primer Primitives CSS imports

## Live updates with Flask-SocketIO (optional)
For live/admin data, use Socket.IO with Flask where sensible.
- Backend (Python): Flask-SocketIO is listed in requirements. Typical setup is to initialize SocketIO with the Flask app and use `socketio.run(app)` instead of `app.run()`.
- Frontend (TypeScript): install `socket.io-client` and connect to the Flask server.

Minimal shape
- Backend:
  - Initialize: `from flask_socketio import SocketIO, emit; socketio = SocketIO(app, cors_allowed_origins='*')`
  - Emit from server: `socketio.emit('event_name', payload)`
  - Run: `socketio.run(app, host='127.0.0.1', port=5000)`
- Frontend:
  - `npm i socket.io-client`
  - `import {io} from 'socket.io-client'; const socket = io('http://127.0.0.1:5000'); socket.on('event_name', handler)`

Keep events small and structured (JSON). Reuse Flask where practical: auth, session, and routes live in Flask; SocketIO is only for data that must be real-time.

## Scripts
- npm run dev — start Vite dev server
- npm run build — type-check and build to `../templates`
- npm run preview — preview built assets locally
- npm run lint — run ESLint

## Part of the larger project
This app lives at `ReactWebpage/` but is part of the bot’s repo. The Flask server picks up production builds from `templates/`. Commit both sides together when you change UI behaviors that depend on backend data.
