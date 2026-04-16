# dZshield (Brahmos) - Enterprise SOC Dashboard & Automated Incident Response Platform
**Project Overview & Architecture Plan**

## 1. Executive Summary
dZshield (Brahmos) is a localized, AI-powered Security Operations Center (SOC) dashboard designed to aggregate, analyze, and act upon network security events in real-time. The platform provides an enterprise-grade interface for monitoring live traffic blocks (allowed, denied, malicious), generating automated mitigation strategies using local LLMs, and exporting professional incident reports for stakeholders.

## 2. Key Objectives & Features
* **Real-time Log Ingestion**: Continuous monitoring of firewall traffic (Windows Advanced Firewall, Fortigate).
* **AI-Powered Analysis**: Integration with LLM agents to provide context-aware, 3-tier security recommendations (Deny, Malicious, Allowed) rather than raw log dumps.
* **Automated Professional Reporting**: Dynamic generation of multi-page, visually rich PDF and Excel incident reports directly from selected log filters and time frames.
* **Streamlined Deployment**: One-click initialization via automated scripting and Docker containerization ensuring 0.0.0.0 binds for seamless cross-network UI access.
* **Visual Data Synchronization**: High-fidelity dashboarding where charts, tables, and geographic flow maps update in tandem with user-selected time slices and data filters.

---

## 3. Architecture & Package Flow (Data Pipeline)

The system is built on a responsive, microservices-driven architecture orchestrating 5 primary layers:

### Phase 1: Data Generation & Ingestion (The Edge)
* **Components**: `log_generator/generate.py`, External Integrations (e.g., Fortigate syslog).
* **Flow**: Security event logs are continuously harvested from the host firewall or external networking devices. Log entries are parsed, standardized into JSON structures, and pushed via HTTP POST requests to the Backend API.

### Phase 2: Core Processing & Logic (The Backend)
* **Components**: Python FastAPI Server (`backend/`), MySQL/SQLite Database.
* **Flow**: 
  * The backend (`port 8000`) receives raw events.
  * It enriches the data (Geo-IP tagging, time-series organization).
  * Data is persisted into the relational database for fast querying and historical tracking.
  * Webhook and API endpoints trigger immediate secondary evaluations if an event exceeds specific threat thresholds.

### Phase 3: AI Correlation & Automation Engine
* **Components**: LLM Agent (`backend/agent.py`), n8n (`port 5678`), Qdrant Vector DB (`port 6333`).
* **Flow**:
  * For critical events, the backend requests an analysis from the AI agent.
  * **Qdrant** provides semantic similarity models for matching current threats with past known event signatures.
  * **n8n** acts as the automation workflow controller, optionally dispatching automated email alerts (e.g., to dedicated security teams) or bridging alerts to external ticketing platforms.
  * The AI produces human-readable narratives and generates actionable remediation playbooks formatted specifically for the incident type.

### Phase 4: Visualization & Threat Management (The Frontend)
* **Components**: React.js / Vite SPA (`frontend/`).
* **Flow**:
  * Running on `port 5173`, the dashboard consumes data streams from the backend via REST endpoints.
  * The UI incorporates a **Zero-Trust Topology Map**, interactive threat charts, and a synchronized data grid.
  * Users can isolate specific timeframe flows, click into deep-dive recommendations, and manage remote mock resources via the integrated sidebars.

### Phase 5: Export & Communication (The Output)
* **Components**: PDF/Excel Render Engine, Notification Service.
* **Flow**:
  * A security analyst defines specific threat parameters in the UI (e.g., filtering all "denied" IPs over the last 24 hours).
  * The frontend triggers an export call; the backend utilizes headless rendering or specific layout algorithms to prevent data clipping and ensures all charts/graphs fit dynamically across multipage PDF/Excel outputs.
  * Finalized threat incident summaries are automatically prepared for email dispatch.

---

## 4. Deployment Pipeline
* **Orchestration**: `docker-compose.yml` ensures isolation, reliable process restarts, and dependency management for all nodes (n8n, Backend, Qdrant, UI).
* **Environment Provisioning**: Administrator rollout scripts (`setup_vm.ps1` / `start_docker_services.ps1`) automatically configure Docker environments, punch appropriate Windows firewall port configurations locally, and instantiate the entire stack seamlessly for VM-hosted, remote-access setups.
