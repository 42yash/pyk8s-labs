# Technical Design Document: PyK8s-Lab (Prototype V0.1)
**Version:** 0.1
**Date:** 2025-07-24
**Status:** Proposed

## 1. EXECUTIVE SUMMARY & PROJECT OVERVIEW

### 1.1 Project Purpose and Goals

PyK8s-Lab is a self-service, on-demand Kubernetes playground designed to provide developers and learners with ephemeral, isolated Kubernetes clusters. The primary goal of this prototype is to validate the core functionality: provisioning and managing temporary Kubernetes clusters through a simple web interface and a command-line tool.

This simplified version focuses on delivering the essential value proposition quickly by reducing architectural complexity and narrowing the feature set to the most critical components.

### 1.2 Key Features (Prototype Scope)

*   **Simplified On-Demand Cluster Provisioning:** Users can create Kubernetes clusters via a web UI or CLI. For the prototype, only the **KinD (Kubernetes in Docker)** provider will be supported.
*   **Ephemeral Environments:** All clusters will have a fixed Time-to-Live (TTL) to ensure automatic cleanup and prevent resource wastage.
*   **Interactive Web UI:** A web-based dashboard for cluster management.
*   **Core CLI:** A functional Command-Line Interface (CLI) for creating, listing, and deleting clusters.
*   **Basic User Management:** Simple email/password registration and login.

### 1.3 Target Audience and Use Cases

*   **Developers:** Quickly spin up a cluster to test an application or experiment with a Kubernetes feature.
*   **Students & Learners:** An accessible way to learn Kubernetes concepts without a complex local setup.

### 1.4 Technology Stack (Prototype)

| Component             | Technology                          | Rationale                                          |
| --------------------- | ----------------------------------- | -------------------------------------------------- |
| **Backend**           | Python, FastAPI                     | High performance, async, unified for REST & WebSockets. |
| **Frontend (Web)**    | TypeScript, React, Next.js          | Modern, efficient framework for web UIs.            |
| **Database**          | PostgreSQL                          | Reliable, mature, and feature-rich relational DB.  |
| **Cache & Tasks**     | Redis                               | Used for caching and as a simple background task broker. |
| **K8s Distribution**  | KinD (Kubernetes in Docker)         | Lightweight, fast, and ideal for a prototype.       |
| **CLI Client**        | Python, Click                       | Powerful and easy-to-use for creating CLIs.        |
| **Deployment**        | Docker, Kubernetes, Helm            | Industry-standard for containerized deployment.    |

### 1.5 Success Metrics (Prototype)

| Metric                        | KPI Target                                  |
| ----------------------------- | ------------------------------------------- |
| **Core Functionality**        | 100% of users can create, view, and delete a cluster. |
| **Cluster Creation Velocity** | P90 for cluster readiness < 3 minutes.      |
| **System Uptime**             | 99.5% availability for the API and UI.      |
| **Resource Cleanup**          | > 95% of expired clusters are terminated automatically. |

## 2. SYSTEM ARCHITECTURE

### 2.1 High-level Architecture

For the prototype, the complex microservices architecture is consolidated into a **simplified monolithic backend**. A single FastAPI application will serve the REST API, manage WebSocket connections, and handle background tasks for cluster provisioning. This approach significantly reduces deployment and operational complexity.

Clients (Web UI, CLI) communicate directly with this backend service, which orchestrates all operations.

### 2.2 Component Interaction Flow

1.  **Request Initiation:** A user initiates a "Create Cluster" request from the React UI or CLI.
2.  **API Service:** The request hits the FastAPI backend. The service authenticates the user and validates the request.
3.  **Database Write:** A new `Cluster` record is created in PostgreSQL with a `PROVISIONING` status.
4.  **Background Task:** The FastAPI service queues a background task in Redis to handle the long-running cluster creation.
5.  **Provisioning Logic:** A worker process, part of the same application, picks up the task and executes the necessary `kind create cluster` command.
6.  **Real-time Updates:** During provisioning, the worker publishes status updates (e.g., `RUNNING`, `ERROR`) to a Redis Pub/Sub channel.
7.  **WebSocket Notification:** The FastAPI application, handling the user's WebSocket connection, receives this Pub/Sub message and pushes the update to the client.
8.  **Client UI Update:** The UI receives the WebSocket event and updates the cluster status in real-time.

### 2.3 Technology Stack Justification

*   **FastAPI Monolith:** Combining API, WebSockets, and background tasks into one service simplifies development, testing, and deployment for a prototype. The performance of FastAPI is more than sufficient for this initial scope.
*   **KinD Only:** Focusing on a single, well-understood Kubernetes provider (KinD) removes the complexity of building abstractions for multiple distributions.
*   **No Service Mesh:** A service mesh like Linkerd is unnecessary for a single-service architecture, avoiding significant configuration overhead.

## 3. TECHNICAL SPECIFICATIONS

### 3.1 Backend Service (FastAPI Application)

*   **API:** A RESTful API for all primary operations (user auth, cluster CRUD). Auto-generated OpenAPI (Swagger) documentation will be available.
*   **Authentication:** Simple JWT Bearer tokens issued by the application upon successful email/password login.
*   **WebSockets:** A single WebSocket endpoint (`/ws`) for pushing real-time status updates to authenticated clients.
*   **Background Tasks:** FastAPI's built-in `BackgroundTasks` or a lightweight library like Dramatiq will be used to run cluster operations asynchronously.

### 3.2 Container Orchestration

*   **Provisioning Logic:** The background worker will generate a unique configuration for a KinD cluster and execute the `kind create cluster` command using a subprocess.
*   **Resource Management (TTL):** Every cluster is created with a `ttl_expires_at` timestamp. A single, scheduled background job will run periodically (e.g., every 5 minutes) to find expired clusters and queue them for termination.
*   **Multi-tenancy Isolation:** Data plane isolation is naturally provided by KinD, as each cluster runs in its own set of Docker containers. Control plane isolation is enforced at the API layer, where authentication middleware ensures users can only access their own resources.

### 3.3 Frontend Application (Web Dashboard)

*   **Framework:** Next.js with the App Router.
*   **State Management:** Redux Toolkit with RTK Query for managing server state and caching API responses.
*   **Functionality:**
    *   Login/Registration pages.
    *   A dashboard to list created clusters.
    *   A button to provision a new cluster.
    *   A view to see cluster details and status.
    *   A button to terminate a cluster.
*   **Real-time Updates:** The UI will connect to the backend WebSocket endpoint to receive live status updates for provisioning clusters.

### 3.4 CLI Client

*   **Framework:** Python with `click` for command structure and `rich` for enhanced terminal output (tables, colors).
*   **Commands:**
    *   `pyk8s auth login`
    *   `pyk8s cluster create --name <name>`
    *   `pyk8s cluster list`
    *   `pyk8s cluster delete <name>`
    *   `pyk8s cluster get-kubeconfig <name>`
*   **Configuration:** The CLI will store the API URL and JWT in a local configuration file (`~/.config/pyk8s-lab/config.yaml`).

## 4. API & DATABASE

### 4.1 REST API Specification

The FastAPI application will expose an OpenAPI specification at `/docs`.
*   **Key Endpoints:**
    *   `/auth/token`: Login to get a JWT.
    *   `/users/register`: Create a new user account.
    *   `/clusters/`: `GET` to list clusters, `POST` to create a new one.
    *   `/clusters/{cluster_id}`: `GET` for details, `DELETE` to terminate.

### 4.2 WebSocket API

*   **Path:** `/ws`
*   **Authentication:** The client will pass its JWT as a query parameter on connection.
*   **Events:** The API will primarily push a single event type: `cluster.status.changed`.

### 4.3 Database Schema

The schema is simplified to support the core features. The `teams` and `team_memberships` tables are removed for the prototype.

*   **Key Tables:**
    *   `users`: Stores `id`, `email`, and `hashed_password`.
    *   `clusters`: Stores `id`, `name`, `status`, `user_id` (foreign key to users), `encrypted_kubeconfig`, and `ttl_expires_at`.

## 5. SECURITY

### 5.1 Authentication and Authorization

*   **Authentication:** A simple, self-contained authentication system. The backend will handle user registration, password hashing (using a strong algorithm like Argon2 or bcrypt), and JWT issuance.
*   **Authorization:** All API endpoints (except login/register) will require a valid JWT. Middleware will ensure a user can only operate on clusters they own.

### 5.2 Secrets Management

*   **Method:** Standard Kubernetes `Secrets` will be used to store sensitive information like database credentials and the secret key for JWT signing. This avoids the complexity of external secret managers like Vault for the prototype.
*   **In-App Secrets:** The `kubeconfig` for each user cluster will be encrypted using a symmetric key (stored in a Kubernetes Secret) before being saved to the database.

## 6. DEPLOYMENT & OPERATIONS

### 6.1 Deployment

*   **Packaging:** The backend application will be containerized using a multi-stage `Dockerfile` to create a small, secure production image.
*   **Deployment:** A single, simplified **Helm chart** will be used to deploy the entire application stack (FastAPI Backend, PostgreSQL, Redis) to a Kubernetes cluster.
*   **Infrastructure:** The system requires a host machine or VM with Docker installed to run the KinD clusters. The main backend application can run on a separate Kubernetes cluster.

### 6.2 Monitoring and Health

*   **Health Checks:** The FastAPI app will expose `liveness` and `readiness` probe endpoints (`/health/live`, `/health/ready`) for Kubernetes to manage its lifecycle.
*   **Logging:** All services will output structured (JSON) logs to standard output for easy collection.
*   **Metrics:** The backend will expose basic metrics (e.g., HTTP request counts, active clusters) via a `/metrics` endpoint for Prometheus scraping.

## 7. TESTING STRATEGY

### 7.1 Unit and Integration Testing

*   **Backend:** `pytest` will be used to test individual functions (unit tests) and service interactions with a test database (integration tests). The goal is to ensure business logic is correct.
*   **Frontend:** `Jest` and `React Testing Library` will be used to test individual UI components.

### 7.2 End-to-End (E2E) Testing

*   **Framework:** Playwright or Cypress.
*   **Core Scenario:** A single E2E test will simulate the primary user journey:
    1. User registers and logs in via the UI.
    2. User creates a cluster.
    3. The test waits for the cluster status to become `RUNNING`.
    4. The test verifies the cluster can be deleted.

This focused E2E test validates that the entire system is working together as expected.