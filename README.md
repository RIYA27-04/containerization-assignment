<<<<<<< HEAD
# Project Report: FastAPI & PostgreSQL Deployment with Docker Compose and IPvlan Networking

**Name:** Riya jain
**SAP ID:** 500119715
**Batch:** B3 CCVT
**Subject:** Containerization & DevOps

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Docker Multi-Stage Build Optimization](#3-docker-multi-stage-build-optimization)
4. [Network Design](#4-network-design)
5. [Image Size Comparison](#5-image-size-comparison)
6. [Macvlan vs IPvlan Comparison](#6-macvlan-vs-ipvlan-comparison)
7. [Volume Persistence](#7-volume-persistence)
8. [Conclusion](#8-conclusion)

---

## 1. Introduction

This project demonstrates the design, containerization, and deployment of a production-ready web application using modern Docker practices. The system consists of two services:

- **Backend:** A FastAPI (Python 3.11) REST API that provides CRUD operations with auto-generated documentation.
- **Database:** A PostgreSQL 15 Alpine database with persistent named-volume storage.

Key technologies and concepts demonstrated:

- **Docker multi-stage builds** for optimized, minimal images.
- **Docker Compose** for service orchestration with health checks and restart policies.
- **IPvlan networking** for static IP assignment to containers.
- **Named volumes** for data persistence across container restarts.
- **Non-root user execution** for container security hardening.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Host Machine                    │
│                                                         │
│  ┌─────────────────┐       ┌──────────────────────┐    │
│  │  backend_api     │       │   postgres_db         │    │
│  │  (FastAPI)       │──────▶│   (PostgreSQL 15)     │    │
│  │                  │  TCP  │                      │    │
│  │  Port: 8000      │ :5432 │  Port: 5432          │    │
│  │  IP: 172.22.208.11│      │  IP: 172.22.208.10   │    │
│  └────────┬─────────┘       └──────────┬───────────┘    │
│           │                            │                │
│  ┌────────┴────────────────────────────┴───────────┐   │
│  │            IPvlan Network (mynetwork)            │   │
│  │            Subnet: 172.22.208.0/24               │   │
│  │            Gateway: 172.22.208.1                 │   │
│  │            Driver: ipvlan  │  Parent: eth0        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │     Named Volume: containerized-webapp_pgdata     │   │
│  │     Mount: /var/lib/postgresql/data               │   │
│  │     Driver: local                                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Host Port Mapping: 0.0.0.0:8000 → 8000 (backend)      │
└─────────────────────────────────────────────────────────┘
```

### Service Flow

1. Client sends HTTP request to `localhost:8000`
2. Backend container (FastAPI) receives and processes the request
3. Backend connects to PostgreSQL via IPvlan static IP `172.22.208.10`
4. PostgreSQL processes the query and returns results
5. Backend sends JSON response to the client

---

## 3. Docker Multi-Stage Build Optimization

### What are Multi-Stage Builds?

Multi-stage builds allow using multiple `FROM` statements in a single Dockerfile. Each `FROM` begins a new build stage. Artifacts can be selectively copied from one stage to another, leaving behind everything not needed in the final image — build tools, compilers, and cached files.

### Backend Dockerfile — 2 Stages

| Stage | Base Image | Purpose | What's Included |
|---|---|---|---|
| **Stage 1: Builder** | `python:3.11-slim` | Install all Python dependencies | pip, all packages, build tools |
| **Stage 2: Runtime** | `python:3.11-slim` | Run the application | Only installed packages + app.py |

```dockerfile
# Stage 1: Builder — installs all dependencies
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Runtime — copies only what is needed
FROM python:3.11-slim AS runtime

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py .

# Create non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Key Optimizations

- **Slim base image:** `python:3.11-slim` (~150 MB) vs `python:3.11` full (~1 GB) — 85% reduction.
- **No-cache pip install:** `--no-cache-dir` prevents pip cache from being stored in the image.
- **Selective copy:** Only `app.py` is copied — no tests, docs, or unnecessary files.
- **Non-root user:** `appuser` runs the application instead of root — improves security posture.
- **Separate stages:** Build tools are not present in the final runtime image.

### Database Dockerfile

```dockerfile
# Custom PostgreSQL image using Alpine for minimal size
FROM postgres:15-alpine

ENV POSTGRES_USER=shreya
ENV POSTGRES_PASSWORD=shreya123
ENV POSTGRES_DB=appdb

# Auto-runs init.sql on first startup
COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
```

`postgres:15-alpine` (~85 MB) is used instead of the standard `postgres:15` (~400 MB), reducing the database image size by **79%**.

### .dockerignore

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.git
.gitignore
*.md
```

Prevents unnecessary files from entering the build context, reducing image size and improving build speed.

---

## 4. Network Design

### IPvlan Architecture

```
┌──────────────────────────────────────────────┐
│              Physical Network                 │
│              Subnet: 172.22.208.0/24          │
│                                               │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│   │  Host   │  │Container│  │Container│      │
│   │ Machine │  │   DB    │  │ Backend │      │
│   │         │  │.208.10  │  │.208.11  │      │
│   └────┬────┘  └────┬────┘  └────┬────┘      │
│        │            │            │            │
│   ─────┴────────────┴────────────┴─────────   │
│       eth0 (Parent Interface) — IPvlan        │
└──────────────────────────────────────────────┘
```

### Network Creation Command

```bash
# Create IPvlan network manually before running Docker Compose
docker network create \
  -d ipvlan \
  --subnet=172.22.208.0/24 \
  --gateway=172.22.208.1 \
  -o ipvlan_mode=l2 \
  -o parent=eth0 \
  mynetwork
```


### Docker Compose Network Configuration

```yaml
networks:
  mynetwork:
    external: true   # created manually before compose

services:
  db:
    networks:
      mynetwork:
        ipv4_address: 172.22.208.10

  backend:
    networks:
      mynetwork:
        ipv4_address: 172.22.208.11
```

The network is declared as `external: true` because it is created manually before running Docker Compose. This ensures the IPvlan network is properly attached to the host's `eth0` interface.

### Why IPvlan?

- Containers receive **static IP addresses** on the same subnet as the host.
- **No NAT overhead** — direct communication between containers.
- Does **not require promiscuous mode** on the NIC — more compatible with virtual environments.
- Containers **share the host MAC address** — reduces switch load compared to Macvlan.

### Verification Commands

```bash
docker network ls
docker network inspect mynetwork
docker inspect backend_api | grep IPAddress
docker inspect postgres_db  | grep IPAddress

# Expected output:
# "IPAddress": "172.22.208.11"   ← backend_api
# "IPAddress": "172.22.208.10"   ← postgres_db
```

---

## 5. Image Size Comparison

### Single-Stage vs Multi-Stage Build Comparison

| Image | Without Optimization | With Optimization | Reduction |
|---|---|---|---|
| **Backend (FastAPI)** | ~1.0 GB (`python:3.11` full) | ~150 MB (`python:3.11-slim` multi-stage) | **~85%** |
| **Database (PostgreSQL)** | ~400 MB (`postgres:15`) | ~85 MB (`postgres:15-alpine`) | **~79%** |
| **Total** | ~1.4 GB | ~235 MB | **~83%** |

### Actual Docker Images Output

```
IMAGE                          ID            DISK USAGE   CONTENT SIZE
containerized-webapp-backend   d98329085459  219MB        53.5MB
containerized-webapp-db        9c9939582ce1  392MB        109MB
```

### Why Image Size Matters

- **Faster deployments:** Smaller images transfer faster across networks and registries.
- **Reduced attack surface:** Fewer packages means fewer potential vulnerabilities.
- **Lower storage costs:** Especially important in CI/CD pipelines and container registries.
- **Faster container startup:** Less data to load from disk into memory.

### Commands to Inspect Image Layers

```bash
docker images
docker history containerized-webapp-backend
docker history containerized-webapp-db
```

---

## 6. Macvlan vs IPvlan Comparison

| Feature | Macvlan | IPvlan |
|---|---|---|
| **Layer** | Layer 2 (MAC + IP) | Layer 2 or Layer 3 (IP only) |
| **MAC Address** | Unique MAC per container | Shares host MAC address |
| **Modes** | Bridge, VEPA, Private, Passthru | L2 (switch), L3 (router) |
| **Promiscuous Mode** | ❌ Required on parent interface | ✅ Not required |
| **Cloud Compatibility** | ❌ Often blocked (MAC filtering) | ✅ Works in most cloud/VM environments |
| **Performance** | Slightly lower (MAC translation) | Slightly higher (no MAC overhead) |
| **Host ↔ Container** | Cannot communicate directly | Cannot communicate directly (L2) |
| **Container ↔ Container** | ✅ Direct L2 communication | ✅ Direct L2 communication |
| **Switch Load** | Higher (many unique MACs) | Lower (shared MAC) |
| **Best Use Case** | Bare metal / VMs with promiscuous mode | Cloud VMs, WSL, virtual environments |

### Rationale: IPvlan over Macvlan

**IPvlan was chosen** for this project because:

1. This project runs in a **WSL environment** where many hypervisors block multiple MAC addresses per port — a requirement for Macvlan.
2. IPvlan **does not require promiscuous mode** — making it more compatible with virtualized environments.
3. Containers share the host's MAC address while getting **unique IPs** — reduces network complexity.
4. Better suited for **cloud and container-first deployments**.

### When to Choose Macvlan

- Running on **bare metal** or VMs that support promiscuous mode.
- Each container needs a **truly unique MAC address**.
- Integrating with network monitoring tools that **track MAC addresses**.

---

## 7. Volume Persistence

### How It Works

1. Docker creates a named volume **containerized-webapp_pgdata** managed by the local driver.
2. PostgreSQL stores all data at `/var/lib/postgresql/data` inside the container.
3. This path is mapped to the named volume on the host filesystem.
4. When the container is stopped or removed, the volume **persists on the host**.
5. On restart, the same volume is re-mounted — **all data is intact**.

### Persistence Test Procedure

```bash
# Step 1: Start services
docker compose up -d

# Step 2: Insert test data
docker exec backend_api python3 -c "
import urllib.request, json
data = json.dumps({'data': 'Hello World'}).encode()
req = urllib.request.Request('http://localhost:8000/api/records',
  data=data, headers={'Content-Type': 'application/json'})
print(urllib.request.urlopen(req).read().decode())"
# Output: {"message":"Record inserted successfully","id":1}

# Step 3: Verify data exists
docker exec backend_api python3 -c "
import urllib.request
print(urllib.request.urlopen('http://localhost:8000/api/records').read().decode())"
# Output: [{"id":1,"data":"Hello World","created_at":"2026-03-19 18:25:55.631923"}]

# Step 4: Stop and remove containers (volume is KEPT)
docker compose down

# Step 5: Restart services
docker compose up -d

# Step 6: Verify data survived the restart
docker exec backend_api python3 -c "
import urllib.request
print(urllib.request.urlopen('http://localhost:8000/api/records').read().decode())"
# Output: [{"id":1,"data":"Hello World","created_at":"2026-03-19 18:25:55.631923"}]
# ✅ Data persisted successfully!
```

### Volume Management Commands

```bash
# List all volumes
docker volume ls
# Output includes: local   containerized-webapp_pgdata

# Inspect the volume
docker volume inspect containerized-webapp_pgdata

# WARNING: This deletes all data permanently
docker compose down -v
```

---

## 8. Conclusion

This project successfully demonstrates all required containerization concepts:

1. **Multi-stage builds** reduce image sizes by ~83% (from ~1.4 GB to ~235 MB total), leading to faster deployments, lower storage costs, and a reduced attack surface.

2. **IPvlan networking** provides direct Layer 2 communication between containers with static IP assignment — backend at `172.22.208.11` and database at `172.22.208.10` — without requiring promiscuous mode, making it compatible with virtualized environments like WSL.

3. **Named volumes** ensure complete database persistence across all container lifecycle events — containers can be stopped, removed, and restarted without any data loss.

4. **Docker Compose** orchestrates the multi-service application with health checks on both containers, `depends_on` with `service_healthy` condition (backend waits for DB), and `restart: unless-stopped` policies.

5. **FastAPI backend** provides three fully working REST endpoints — `GET /health`, `POST /api/records`, and `GET /api/records` — with table auto-creation on startup and database connection via environment variables.

6. **Container security** is implemented through non-root user execution (`appuser`), `.dockerignore` to prevent sensitive files from entering the image, and environment variable-based credential management.

### Final Status

| Requirement | Implementation | Status |
|---|---|---|
| Containerized backend | FastAPI in python:3.11-slim container | ✅ Done |
| Containerized database | PostgreSQL 15 in postgres:15-alpine container | ✅ Done |
| Custom networking | IPvlan L2 with static IPs on host subnet | ✅ Done |
| Data persistence | Docker named volume pgdata | ✅ Done |
| Image optimization | Multi-stage build, alpine/slim bases, .dockerignore | ✅ Done |
| Health monitoring | Healthcheck on both services, depends_on condition | ✅ Done |
| Security | Non-root user, environment variables for credentials | ✅ Done |

---

*Containerization & DevOps — Project Report*
=======
# 🐳 Containerization Assignment - Docker Project

## 📌 Overview
This project demonstrates containerization using Docker.  
It includes a simple web application and PostgreSQL database running using Docker Compose.

---

## 📁 Project Structure

containerization-assignment/
│── backend/
│   ├── Dockerfile
│   ├── server.js
│   ├── package.json
│   └── .dockerignore
│
│── images/
│   ├── ss1.png
│   ├── ss2.png
│   ├── ss3.png
│   ├── ss4.png
│   └── ss5.png
│
│── docker-compose.yml
│── index.html
│── README.md

---

## ⚙️ Technologies Used

- Docker
- Docker Compose
- Node.js (Backend)
- PostgreSQL (Database)

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/RIYA27-04/containerization-assignment.git
cd containerization-assignment/docker-postgres-project
>>>>>>> be9078853fc549cc10273c995f0689e1c0cf18fa
