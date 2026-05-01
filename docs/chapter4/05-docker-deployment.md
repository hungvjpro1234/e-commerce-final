# Chapter 4 Phase 5 Docker Deployment

## 1. Purpose

This phase completes the Dockerization layer for Chapter 4 at the deployment-structure level. The objective is to ensure the full system can be understood and started from a consistent Docker Compose workflow, with the dedicated gateway included in the stack.

The phase focuses on:

- Compose topology completeness
- gateway integration into the stack
- explicit internal network definition
- environment organization
- reproducible build and run instructions

## 2. Deliverables

### Files added

- `.env.example`
- `docs/chapter4/05-docker-deployment.md`

### Files updated

- `docker-compose.yml`
- `frontend/.env.production`

### Existing runtime artifacts reused in this phase

- `gateway/Dockerfile`
- `user-service/Dockerfile`
- `product-service/Dockerfile`
- `cart-service/Dockerfile`
- `order-service/Dockerfile`
- `payment-service/Dockerfile`
- `shipping-service/Dockerfile`
- `ai-service/Dockerfile`
- `frontend/Dockerfile`

## 3. What was completed in this phase

### 3.1 Gateway added to the Compose stack

The stack now includes a dedicated `gateway` service:

- build context: `./gateway`
- container port: `80`
- host port: `8080`
- depends on all main backend services including `ai-service`

This is the first phase where the Nginx gateway becomes part of the deployment topology instead of only existing as a standalone configuration file.

### 3.2 Frontend now targets gateway inside Compose

`frontend/.env.production` now points all backend base URLs to:

- `http://gateway/api`

This keeps the current frontend proxy layer functional while ensuring backend traffic in the Compose network flows through the Chapter 4 gateway.

### 3.3 Explicit internal network

The Compose stack now declares:

- `ecom-network`

All services, databases, dependencies, gateway, and frontend are attached to this shared bridge network.

This makes the intended Docker topology explicit instead of relying only on Compose defaults.

### 3.4 Root environment reference

A root `.env.example` has been added to provide:

- public port reference
- shared JWT and internal service auth values
- a single high-level entry point for environment documentation

Detailed runtime values remain owned by each service-level `.env.example`, which preserves the existing structure without destructive refactoring.

## 4. Current Compose topology

### 4.1 Application services

| Service | Container port | Host port | Role |
| --- | --- | --- | --- |
| `gateway` | `80` | `8080` | primary backend ingress |
| `frontend` | `3000` | `3000` | user-facing UI |
| `product-service` | `8001` | `8001` | product catalog |
| `user-service` | `8002` | `8002` | auth and user management |
| `cart-service` | `8003` | `8003` | cart operations |
| `order-service` | `8004` | `8004` | checkout orchestration |
| `payment-service` | `8005` | `8005` | payment processing |
| `shipping-service` | `8006` | `8006` | shipment management |
| `ai-service` | `8007` | `8007` | recommendation and chatbot |

### 4.2 Databases and infrastructure dependencies

| Service | Engine | Container port | Host port |
| --- | --- | --- | --- |
| `product-db` | PostgreSQL | `5432` | `5432` |
| `ai-db` | PostgreSQL | `5432` | `5433` |
| `user-db` | MySQL | `3306` | `3307` |
| `cart-db` | MySQL | `3306` | `3308` |
| `order-db` | MySQL | `3306` | `3309` |
| `payment-db` | MySQL | `3306` | `3310` |
| `shipping-db` | MySQL | `3306` | `3311` |
| `neo4j` | Neo4j | `7474`, `7687` | `7474`, `7687` |

## 5. Build and run procedure

### 5.1 Full system build

From the repository root:

```bash
docker compose build
```

### 5.2 Full system startup

```bash
docker compose up
```

Detached mode:

```bash
docker compose up -d
```

### 5.3 Suggested first verification steps

After startup:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/products/products
```

Frontend:

- `http://localhost:3000`

Gateway:

- `http://localhost:8080`

## 6. Startup behavior by service

### 6.1 Django services

Each Django business service currently starts by:

1. waiting for its database socket to become reachable
2. running `python manage.py migrate`
3. running `python manage.py seed_data`
4. starting `runserver` on `0.0.0.0`

This behavior is encoded directly in `docker-compose.yml`.

### 6.2 AI service

`ai-service` currently starts by:

1. waiting for `ai-db`
2. starting `uvicorn`

### 6.3 Gateway

`gateway` starts from the custom `gateway/Dockerfile` and loads:

- `gateway/nginx.conf`

### 6.4 Frontend

`frontend` uses its production image and environment file:

- `frontend/.env.production`

Within Compose, that environment now targets `gateway` as the backend ingress.

## 7. Environment organization

### 7.1 Root-level reference

The new root `.env.example` acts as the top-level deployment reference.

It documents:

- public ports
- database ports
- shared auth values

### 7.2 Service-level ownership

Detailed service runtime configuration remains in:

- `user-service/.env.example`
- `product-service/.env.example`
- `cart-service/.env.example`
- `order-service/.env.example`
- `payment-service/.env.example`
- `shipping-service/.env.example`
- `ai-service/.env.example`
- `frontend/.env.production`

This split is intentional because the project already has a stable per-service configuration model.

## 8. Dependency notes

### 8.1 Application dependencies

- `order-service` depends on:
  - `order-db`
  - `cart-service`
  - `payment-service`
  - `product-service`
  - `shipping-service`
- `ai-service` depends on:
  - `ai-db`
  - `neo4j`
  - `product-service`
  - `order-service`
- `gateway` depends on all primary backend APIs
- `frontend` depends on `gateway` and the core backend services

### 8.2 Limitation of current `depends_on`

`depends_on` in the current Compose file guarantees startup order, not application readiness. The repository partially compensates for this by using explicit wait loops in the Django and AI service startup commands.

The stack does not yet define full Docker healthchecks for all services in this phase.

## 9. Common issues and handling

### 9.1 Port conflicts

If local services already occupy ports such as `3000`, `5432`, or `8080`, Compose startup will fail. Resolve by stopping the conflicting local process or adjusting the published host port.

### 9.2 Slow first build

The first `docker compose build` may take noticeably longer because it builds:

- multiple Django images
- the frontend production image
- the gateway image
- the AI service image

This is expected.

### 9.3 Database initialization delay

Even with `depends_on`, databases may need a short warm-up period. The Django services already wait for a reachable DB socket before running migrations.

### 9.4 Frontend cannot call backend

If the frontend starts but API requests fail:

1. verify `gateway` is running
2. verify `frontend/.env.production` still points to `http://gateway/api`
3. verify gateway route mapping in `gateway/nginx.conf`

### 9.5 AI service issues

If AI endpoints fail:

1. verify `ai-db` and `neo4j` are up
2. verify `product-service` is reachable
3. check `ai-service/.env.example` values

## 10. Assessment against the Phase 5 prompt

| Prompt requirement | Status | Notes |
| --- | --- | --- |
| Dockerfile for each main service | achieved | already present; gateway also included |
| `docker-compose.yml` | achieved | updated and remains authoritative |
| internal network | achieved | explicit `ecom-network` added |
| volumes and env structure | achieved at project level | service env files plus root env reference |
| databases and dependencies declared | achieved | all core services and infra are present |
| startup commands clearly recorded | achieved | encoded in compose and described here |
| full system can be started with one command | achieved in deployment structure | `docker compose up` |

## 11. Remaining gaps after Phase 5

- full runtime verification output has not yet been captured in Chapter 4 evidence form
- gateway smoke-test results are not yet stored under `docs/chapter4/evidence/`
- healthcheck definitions are still not standardized across all services
- frontend still uses its internal proxy layer, though it now points to the real gateway inside Compose

These are acceptable at this stage and will be addressed by later phases, especially end-to-end testing and observability.
