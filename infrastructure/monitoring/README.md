# Monitoring Skeleton

This directory contains the monitoring skeleton for Chapter 4 observability.

## Current state

- Gateway logging is implemented in `gateway/nginx.conf`.
- Application logging is configured in the Django services and in `ai-service`.
- Health endpoints exist across the gateway and the application services.
- Full Prometheus-native metrics endpoints are not yet implemented across all services.

## Why this is a skeleton

The project now has enough structure to support later monitoring work, but it does not yet claim a complete production-grade metrics stack. The included `prometheus.yml` documents the intended scrape topology and provides a stable location for later expansion.

## Intended next steps

- add `/metrics` endpoints or exporters where appropriate
- add a Prometheus service to Docker Compose if full monitoring is required
- optionally add Grafana dashboards for demo visualization
