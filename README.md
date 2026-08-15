# JaFaFaWeb

JaFaFaWeb is the web interface for **JaFaFa**, a vehicle telemetry and fleet-monitoring platform.

The project currently provides two browser-based interfaces:

- **`index.html`** — the JaFaFa admin/fleet command center for managing customers, vehicles, telemetry, alerts, claims, and fleet health.
- **`customer.html`** — the customer portal for accounts, vehicle access, health, alerts, and telemetry history.
- **`indexboring.html`** and **`customerboring.html`** — plain/reference versions kept separately from the primary UI.

## Current architecture

The current prototype is intentionally lightweight and is built primarily as two self-contained HTML applications with embedded CSS and JavaScript. Telemetry is normalized through a shared JaFaFa health/telemetry model so the admin and customer interfaces can present consistent vehicle status.

The production architecture is intended to evolve toward:

```text
Vehicle / OBD
     ↓
JaFaFa client
     ↓
JaFaFa backend
     ↓
Admin portal ──────→ fleet/customer management
     ↓
Customer portal ───→ vehicle health and telemetry
```

## Key capabilities

### Admin portal

- Fleet overview and fleet health
- Live/recent/stale/offline telemetry states
- Customer and vehicle management
- Vehicle telemetry inspection
- Alerts and claims
- Ownership-conflict detection
- Google sign-in entry point for administrators
- Responsive/mobile navigation
- Telemetry visualizations and command-center UI

### Customer portal

- Customer account/sign-in experience
- Google sign-in option
- Personal vehicle garage
- Vehicle health and status
- Human-readable telemetry health categories
- Alerts and telemetry history
- Vehicle claim/request flow
- Responsive mobile experience

## Development notes

This repository is currently a frontend prototype. Authentication, authorization, ownership decisions, password handling, and telemetry ingestion should ultimately be enforced by a trusted backend rather than relying on browser-local state.

The `*boring.html` files are intentionally retained as plain/reference implementations and should not be treated as generated build artifacts.

## Validation

Pull requests run the repository validation workflow under `.github/workflows/validate-pr.yml`. It checks the HTML document structure and JavaScript syntax in the primary admin and customer applications.

## Repository

JaFaFaWeb is maintained as part of the JaFaFa vehicle telemetry project.
