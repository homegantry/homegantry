# Homegantry Backlog

## Kanban Status (Feb 24, 2026)

### 📋 Backlog (To Do)
- [ ] **AI Widget Suggestions** - Context-aware widget recommendations based on time of day/user behavior
- [ ] **Voice Control Integration** - TTS/STT for hands-free dashboard interaction
- [ ] **Energy Monitoring Dashboard** - Track power consumption across devices
- [ ] **Smart Notifications** - AI-filtered alerts that learn what's important
- [ ] **Calendar Widget** - Unified calendar view with agenda
- [ ] **Weather-Aware Dashboard** - Widgets adapt based on current weather conditions
- [ ] **Local AI Privacy Mode** - Run AI features locally (Ollama) for privacy-sensitive users

### 🚧 In Progress
- [ ] **Core Dashboard Layout** - Basic SvelteKit + FastAPI structure (MVP)

### ✅ Done
- [ ] Project setup (Docker Compose, Nginx, Frontend, Backend)
- [ ] Basic authentication (Authentik integration)
- [ ] Workspace mounting for file access

---

## Feature Ideas (Added Today)

### 1. AI Widget Suggestions
**Priority:** Medium | **Category:** AI Enhancement
- Context-aware widget recommendations
- Learns from user behavior (time of day, frequently accessed pages)
- Suggests relevant widgets based on patterns

### 2. Energy Monitoring Dashboard
**Priority:** Low | **Category:** Home Integration
- Integrate with home energy monitors (Shelly EM, Sense, etc.)
- Real-time power consumption tracking
- Historical graphs and cost estimation
- Alerts for unusual consumption

### 3. Weather-Aware Dashboard (NEW)
**Priority:** Medium | **Category:** Context Awareness
- Fetch local weather data (OpenWeatherMap or local weather station)
- Auto-adjust dashboard based on conditions:
  - Nice weather → show outdoor cameras, garden sensors
  - Cold/rainy → show heating controls, indoor air quality
  - Sunny → solar production stats
- Configurable rules for different conditions

### 4. Local AI Privacy Mode (NEW)
**Priority:** Low | **Category:** Privacy & AI
- Integrate Ollama or similar for local LLM inference
- Keep all AI processing on-premises (no cloud AI calls)
- Useful for:
  - Privacy-conscious users
  - Offline operation
  - Cost savings on API calls
- Toggle in settings to switch between local/cloud AI

---

*Last Updated: 2026-02-24*
