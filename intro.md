# 🚀 FastAPI & PostgreSQL Deployment with Docker Compose and IPvlan Networking

---

**Name:** Riya Jain
**Batch:** 3
**SAP ID:** 500119715

---

## 🌐 Live Project Access

**Interactive Project Website:**
[https://riya27-04.github.io/containerization-assignment/index.html](https://riya27-04.github.io/containerization-assignment/index.html)

This live site includes:

- Full system architecture diagram
- Step-by-step setup with terminal outputs
- API endpoint documentation
- IPvlan vs Macvlan comparison
- Docker image optimization results

---

## 📂 Repository Quick Access

| Resource | Link |
|---|---|
| Project Website | [Live Site](https://riya27-04.github.io/containerization-assignment/index.html) |
| Detailed Report | `REPORT.md` |
| Docker Compose | `docker-compose.yml` |
| Backend Code | `backend/app.py` |
| Backend Dockerfile | `backend/Dockerfile` |
| Docker Ignore | `backend/.dockerignore` |
| Database Init Script | `database/init.sql` |

---

## 📌 Introduction

In modern software development, containerization has become an essential approach for building, deploying, and managing applications efficiently. This project demonstrates how to containerize a backend web application along with a database service using Docker and Docker Compose.

The application is developed using **FastAPI**, a modern Python web framework, and **PostgreSQL**, a powerful relational database. Both services are containerized and communicate through Docker networking.

Best practices such as multi-stage builds, non-root user execution, and image optimization have been applied to ensure that the application is secure, lightweight, and production-ready.

---

## 🎯 Project Objectives

- Understand Docker containerization
- Build and deploy a FastAPI backend
- Integrate PostgreSQL database
- Use Docker Compose for orchestration
- Implement persistent storage using volumes
- Configure networking between containers
- Optimize Docker images
- Apply security best practices

---

## 🧱 System Architecture Overview

```
Client (Browser / Postman)
        │
        │  HTTP Request
        ▼
FastAPI Backend Container
      (Port: 8000)
        │
        │  SQL Queries
        ▼
PostgreSQL Database Container
      (Port: 5432)
        │
        ▼
Docker Volume (pgdata)
  Persistent Storage
```

---

## ⚙️ Technology Stack

| Component | Technology |
|---|---|
| Backend | FastAPI (Python 3.10) |
| Database | PostgreSQL 15 (Alpine) |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Networking | IPvlan |
| Storage | Docker Volume |

---

## ⚡ Application Functionality

| Endpoint | Route | Method | Description |
|---|---|---|---|
| Home | `/` | GET | Returns a welcome message |
| Health Check | `/health` | GET | Returns API status |
| Add Data | `/add` | POST | Inserts data into database |
| Fetch Data | `/data` | GET | Returns all stored records |

---

## 🔄 Database Logic

- Uses `psycopg2` for database connection
- Retry mechanism handles DB startup delay
- Table is created automatically on startup

**Table Structure:**

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary Key |
| `name` | Text | Text field |
| `created_at` | Timestamp | Record creation time |

---

## 🐳 Docker Implementation

- Multi-stage build used to reduce image size
- `python:3.10-slim` base image used
- Dependencies installed in builder stage
- Only required files copied to final image

---

## 🔒 Security Features

- Non-root user (`appuser`) used
- Prevents privilege escalation
- Safer container execution

---

## 🌐 Networking

IPvlan networking is used for communication between containers.

**Benefits:**
- Lower network overhead
- Better scalability
- Suitable for VM/cloud environments

---

## 💾 Data Persistence

- Docker named volume used
- Data remains after container restart
- Ensures reliability

---

## 🆚 IPvlan vs Macvlan

| Feature | Macvlan | IPvlan |
|---|---|---|
| MAC Address | Unique per container | Shared MAC address |
| Network Load | Higher | Lower |
| Scalability | Less scalable | More scalable |
| Best For | Physical network integration | VM/cloud environments |

> **Conclusion:** IPvlan is better suited for this project.

---

## ✅ Key Achievements

- ✔️ FastAPI backend containerized
- ✔️ PostgreSQL integrated
- ✔️ Docker Compose orchestration
- ✔️ Persistent storage implemented
- ✔️ Secure container setup
- ✔️ Optimized Docker images
- ✔️ Working API endpoints

---

## 📌 Conclusion

This project demonstrates a complete containerized backend system using modern tools and practices. It shows how Docker can simplify deployment, improve consistency, and make applications scalable and secure.

The integration of **FastAPI**, **PostgreSQL**, **Docker Compose**, and networking concepts makes this project a strong example of real-world DevOps implementation.