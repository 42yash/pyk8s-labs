## **Technical Design Document: PyK8s-Lab (V1.0)**

**Version:** 1.0
**Status:** Proposed

### **1. Introduction & Vision**

#### **1.1. Project Purpose and Goals**

PyK8s-Lab is a self-service, on-demand Kubernetes playground designed to provide developers, students, and DevOps engineers with ephemeral, isolated Kubernetes clusters. The primary goal is to accelerate learning, experimentation, and the testing of cloud-native applications.

This document outlines the evolution of the existing prototype into a feature-complete V1.0 release. We will build upon the prototype's validated core functionality to deliver a stable, scalable, and user-friendly platform.

#### **1.2. Key Features & Capabilities (V1.0 Scope)**

The V1.0 release will include all features currently implemented in the prototype and introduce new capabilities to enhance collaboration and flexibility.

*   **Core (Implemented in Prototype):**
    *   **User Authentication:** Secure user registration and JWT-based login.
    *   **On-Demand Cluster Provisioning:** Creation of clusters using KinD (Kubernetes in Docker).
    *   **Time-to-Live (TTL):** Automatic scheduling of cluster deletion to prevent resource wastage.
    *   **Web UI Dashboard:** A React-based dashboard for listing, creating, and deleting clusters.
    *   **Real-time Updates:** WebSocket integration for instant, push-based updates on cluster status changes (e.g., `PROVISIONING` to `RUNNING`).
    *   **CLI Client:** A Python-based CLI for authentication and essential cluster management.

*   **New & Enhanced Features (Planned for V1.0):**
    *   **Multi-Provider Support:** Introduce support for other lightweight Kubernetes distributions like k3s or MicroK8s, selectable at creation time.
    *   **Team Management & Quotas:** Allow users to create teams, invite members, share cluster resources, and operate under defined usage quotas.
    *   **Expanded CLI Functionality:** Enhance the CLI with commands for team administration and advanced cluster configuration.
    *   **Interactive Web Terminal:** Provide direct `kubectl` access to provisioned clusters from within the web UI.

#### **1.3. Technology Stack**

The technology stack proven in the prototype will be retained and scaled for the V1.0 release.

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend** | Python, FastAPI, SQLAlchemy | High performance, async-native, and robust for API development. |
| **Frontend (Web)** | JavaScript, React, Next.js, Redux Toolkit | Modern, efficient, and scalable for building interactive user interfaces. |
| **Database** | PostgreSQL | A reliable and feature-rich relational database for persistent storage. |
| **Cache & Messaging** | Redis | Used for WebSocket Pub/Sub messaging and as a potential caching layer. |
| **K8s Distribution** | KinD (Kubernetes in Docker) | The initial, validated provider, ideal for rapid, Docker-based provisioning. |
| **CLI Client** | Python, Click, Rich | Powerful and user-friendly for creating an enhanced terminal experience. |
| **Deployment** | Docker, Docker Compose, Helm | Standard for containerization, local development, and production deployments. |

### **2. System Architecture**

#### **2.1. High-Level Architecture**

The V1.0 architecture is a direct evolution of the successful prototype design. It consists of a monolithic but modular backend service, a decoupled frontend, and a command-line interface. This approach maintains simplicity for development and deployment while providing a clear path for future scalability.

The main components are:
*   **FastAPI Backend:** A single, powerful service that exposes a REST API for core operations, handles WebSocket connections for real-time updates, and manages the lifecycle of clusters via background tasks.
*   **Next.js Frontend:** A server-rendered React application that provides the primary web dashboard.
*   **CLI Client:** A standalone Python application for power users and automation.
*   **Supporting Services:** PostgreSQL for data persistence and Redis for the Pub/Sub messaging that powers real-time UI updates.

#### **2.2. Component Interaction Flow**

The core user flow for creating a cluster has been validated by the prototype and remains the central workflow:

1.  **Request Initiation:** A user logs in and initiates a "Create Cluster" request from the React UI or the CLI.
2.  **API Service:** The request hits the `POST /api/v1/clusters` endpoint on the FastAPI backend. The service authenticates the user's JWT and validates the request payload (e.g., cluster name constraints).
3.  **Database Write:** A new `Cluster` record is created in the PostgreSQL database with a `PROVISIONING` status via `crud.py`. The cluster is linked to the authenticated user's ID.
4.  **Real-time Feedback:** A status update is immediately published to the `cluster-status` Redis channel, notifying the UI via WebSocket that provisioning has begun.
5.  **Asynchronous Provisioning:** The API endpoint uses FastAPI's `BackgroundTasks` to schedule the `run_cluster_provisioning` task. This ensures the API responds instantly to the user.
6.  **Provisioning Execution:** The background task calls the `provisioner.py` module, which executes the `kind create cluster` command in a separate thread to avoid blocking the server's event loop.
7.  **Status Updates & Kubeconfig:** Upon completion, the provisioner retrieves the cluster's kubeconfig, encrypts it, and updates the cluster's database record with the new status (`RUNNING` or `ERROR`) and the encrypted kubeconfig.
8.  **Final Notification:** A final status update is published to Redis and pushed to the client, causing the UI to update automatically.

#### **2.3. Asynchronous Task & Lifecycle Management**

The system relies on two key asynchronous mechanisms to manage long-running operations and resource cleanup:

*   **Provisioning & Deletion:** Long-running tasks are handled by FastAPI's `BackgroundTasks` feature. Blocking I/O operations within these tasks, such as running `subprocess` commands in `provisioner.py`, are delegated to a separate thread pool using `asyncio.to_thread`. This keeps the main application responsive and non-blocking.
*   **TTL & Cleanup:** A scheduled job, managed by `apscheduler` and configured in the `main.py` lifespan event handler, runs every five minutes. This job, `check_expired_clusters`, queries the database for clusters whose `ttl_expires_at` timestamp is in the past, and for each one found, it schedules the `run_cluster_deletion` background task to ensure automatic resource cleanup.

### **3. Backend & API Specifications**

#### **3.1. Database Schema**

The database schema will be expanded from the prototype's foundation to include entities for team collaboration.

*   **Existing Tables (from Prototype):**
    *   `users`: Stores `id` (UUID), `email`, and `hashed_password`.
    *   `clusters`: Stores `id` (UUID), `name`, `status`, `encrypted_kubeconfig`, `ttl_expires_at`, and a `user_id` foreign key. The relationship is accessible via `user.clusters` and `cluster.owner`.

*   **New Tables (for V1.0):**
    *   `teams`: Will store `id` (UUID) and `name`.
    *   `team_memberships`: A join table to establish a many-to-many relationship between users and teams, storing `user_id`, `team_id`, and a `role` (e.g., 'admin', 'member').
    *   *Future Consideration:* A `quotas` table could be added to define resource limits (e.g., max clusters, max CPU) for users or teams.

*   **Updated Entity-Relationship Diagram (V1.0):**

    ```mermaid
    erDiagram
        users {
            UUID id PK
            String email UK
            String hashed_password
        }

        teams {
            UUID id PK
            String name UK
        }

        team_memberships {
            UUID user_id PK, FK
            UUID team_id PK, FK
            String role
        }

        clusters {
            UUID id PK
            String name
            String status
            String encrypted_kubeconfig
            timestamptz ttl_expires_at
            UUID user_id FK
            UUID team_id FK "nullable"
        }

        users ||--o{ team_memberships : "has"
        teams ||--o{ team_memberships : "has"
        users ||--o{ clusters : "owns"
        teams ||--o{ clusters : "can own"

    ```

#### **3.2. REST API Specification (OpenAPI)**

The API will be versioned under `/api/v1`.

*   **Existing Endpoints:**
    *   `POST /users/register`: Create a new user account.
    *   `POST /auth/token`: Log in to receive a JWT.
    *   `GET /clusters`: List all clusters owned by the authenticated user.
    *   `POST /clusters`: Create a new cluster. Responds with `202 ACCEPTED`.
    *   `DELETE /clusters/{cluster_id}`: Schedule a cluster for deletion. Responds with `202 ACCEPTED`.

*   **New & Formalized Endpoints:**
    *   `GET /clusters/{cluster_id}/kubeconfig`: Retrieves the decrypted kubeconfig file as plain text for a running cluster.
    *   `POST /teams`: Create a new team, making the authenticated user the first admin.
    *   `GET /teams`: List all teams the authenticated user is a member of.
    *   `POST /teams/{team_id}/members`: Invite a user to a team by email. (Requires admin role).
    *   `DELETE /teams/{team_id}/members/{user_id}`: Remove a member from a team. (Requires admin role).

#### **3.3. WebSocket API**

The WebSocket API provides real-time updates to connected clients.

*   **Endpoint:** `/ws`
*   **Authentication:** The client must provide a valid JWT as a query parameter (`?token=...`) upon connection. The connection will be rejected if the token is missing or invalid.
*   **Existing Events:**
    *   **Cluster Status Change:** The backend pushes a JSON message when a cluster's status changes. The message format is `{"user_id": "...", "cluster_id": "...", "status": "..."}`. A special status of `"DELETED"` instructs the client to remove the cluster from its state.
*   **Proposed New Events:**
    *   `team.user.joined`: Notifies team members that a new user has joined.
    *   `team.cluster.created`: Notifies team members that a new cluster has been created for the team.
    
### **4. Frontend & User Experience**

The user experience is delivered through two primary clients: a web-based dashboard and a command-line interface. Both are built upon the V1.0 backend APIs.

#### **4.1. Web Dashboard (Next.js)**

The web dashboard is the primary graphical interface for users to interact with PyK8s-Lab.

*   **Current State (from Prototype):**
    The prototype includes a functional Next.js application with a robust foundation. It successfully implements user registration, login, and a protected dashboard route. The dashboard uses RTK Query to fetch a user's clusters, displays them in a list with real-time status updates powered by a WebSocket connection, and allows for cluster creation and deletion. State persistence for authentication is handled via `redux-persist`.

*   **V1.0 Enhancements:**
    *   **Team Management:** New pages and components will be added to the dashboard to manage teams.
        *   A "Teams" section will allow users to view teams they belong to, create new teams, and invite members by email.
        *   A modal or dedicated page will be used for the team creation form.
        *   Team settings will include a member list with roles and options to manage membership (e.g., remove member, change role).
    *   **Kubeconfig Access:** Within each cluster's detail view, a "Get Kubeconfig" button will be added. This button will make an authenticated call to the `GET /clusters/{cluster_id}/kubeconfig` endpoint and provide the user with the credentials, likely via a "copy to clipboard" action or a direct file download.
    *   **Interactive Terminal:** A web-based terminal will be integrated to provide direct shell access to running clusters. This will be implemented using a library like **Xterm.js** and will connect to a dedicated WebSocket endpoint on the backend that can stream TTY data from the cluster.

#### **4.2. State Management (Redux Toolkit)**

The frontend's state is managed centrally using Redux Toolkit, providing a predictable and scalable pattern.

*   **Current Setup:**
    *   **`apiSlice.js`:** Defines all interactions with the backend REST API using RTK Query. It handles data fetching, caching, and invalidation for clusters. It also contains the WebSocket client logic within the `onCacheEntryAdded` lifecycle hook to receive and process real-time status updates.
    *   **`authSlice.js`:** Manages user authentication state, including the user object and the JWT. This slice is persisted to `localStorage` via `redux-persist` to keep users logged in across browser sessions.
    *   **`store.js`:** Configures the Redux store, combines the reducers, and sets up the persistence layer.

*   **V1.0 Expansion:**
    *   The `apiSlice` will be expanded with new endpoints for all team-related operations (`getTeams`, `createTeam`, `inviteMember`, etc.).
    *   The `authSlice` may be updated to include the user's current team context or roles to enable role-based rendering of UI components.
    *   UI state for new modals and forms (e.g., the "Create Team" modal) will be managed locally within the relevant React components using `useState`.

#### **4.3. Command-Line Interface (CLI)**

The CLI provides a fast and scriptable interface for power users and automation.

*   **Current State (from Prototype):**
    The existing CLI (`cli/main.py`) is a functional Python application using `click` for command structure and `rich` for enhanced terminal output. It supports:
    *   `pyk8s auth login`: Authenticates and saves the JWT to `~/.config/pyk8s-lab/config.yaml`.
    *   `pyk8s cluster list`: Displays clusters in a formatted table.
    *   `pyk8s cluster create`: Provisions a new cluster.
    *   `pyk8s cluster delete`: Schedules a cluster for deletion.
    *   `pyk8s cluster get-kubeconfig`: Prints a cluster's kubeconfig to standard output.

*   **V1.0 Enhancements:**
    The CLI will be expanded with a new `team` command group to mirror the new API capabilities:
    *   `pyk8s team create <team-name>`
    *   `pyk8s team list`
    *   `pyk8s team invite <user-email> --role [admin|member]`
    *   `pyk8s team members <team-name>`
    Additionally, the `cluster create` command will be updated to support team ownership and multiple providers:
    *   `pyk8s cluster create --name <name> --team <team-name> --provider [kind|k3s]`

### **5. Deployment & Operations**

The deployment strategy ensures a consistent environment for local development and a scalable, robust architecture for production.

#### **5.1. Development Environment (Docker Compose)**

The local development environment is fully defined and automated using Docker Compose, as specified in the root `docker-compose.yml` file.

*   **Services:** The file orchestrates the four primary services: `backend`, `frontend`, `db` (PostgreSQL), and `redis`.
*   **Permissions Handling:** The `scripts/set_env.sh` helper script correctly detects the host's Docker group ID (`DOCKER_GID`) and user ID (`UID`), writing them to a `.env` file. The `docker-compose.yml` file then passes these values as build arguments to the backend's Dockerfile. This critical step ensures the backend container's non-root user has the correct permissions to interact with the host's Docker socket (`/var/run/docker.sock`) for provisioning KinD clusters.
*   **Lifecycle Scripts:** The development workflow is streamlined with helper scripts:
    *   `./restart.sh`: The standard command for stopping, building any changed images, restarting services, and applying database migrations.
    *   `./clean-restart.sh`: A "nuke and pave" script that removes all containers, volumes, and caches before rebuilding the environment from scratch.

#### **5.2. Production Deployment (Helm)**

For production, the application will be packaged as a Helm chart, enabling repeatable and configurable deployments to any Kubernetes cluster.

*   **Chart Structure:** A parent Helm chart named `pyk8s-lab` will be created. This chart will manage the deployment of the application's components as sub-charts and will manage dependencies on third-party charts.
*   **Key `values.yaml` Parameters:** The deployment will be highly configurable through the `values.yaml` file, allowing operators to set:
    *   Image tags for each service (`backend.image.tag`, `frontend.image.tag`).
    *   Replica counts for horizontal scaling (`backend.replicaCount`).
    *   Resource requests and limits (`backend.resources`).
    *   Ingress configuration, including hostnames and TLS settings.
    *   Configuration for external services (e.g., disabling the in-cluster PostgreSQL and Redis charts to use a managed cloud database).

#### **5.3. Monitoring & Health**

To ensure operational stability in a production environment, the backend application will expose health check endpoints for Kubernetes to use.

*   **Liveness Probe:** An endpoint at `/health/live` will be added to the FastAPI application. This endpoint will return a `200 OK` response to indicate that the application process is running. If this probe fails, Kubernetes will restart the container.
*   **Readiness Probe:** An endpoint at `/health/ready` will be added. This probe will perform more comprehensive checks, such as verifying connectivity to the PostgreSQL database and Redis. If this probe fails, Kubernetes will stop sending traffic to the pod until it becomes ready again. This prevents requests from being sent to a pod that is not fully initialized or has lost its critical dependencies.

### **6. Testing Strategy**

A multi-layered testing strategy is essential to ensure the reliability, robustness, and correctness of the V1.0 release. The testing approach is designed to catch bugs early, prevent regressions, and validate that all components of the system work together as expected.

#### **6.1. Backend Testing (`pytest`)**

The backend will be tested at both the unit and integration levels using the `pytest` framework.

*   **Unit Tests:** These tests will focus on individual functions and business logic in isolation, mocking any external dependencies like the database or `subprocess` calls. Key areas for unit testing include:
    *   **`core/security.py`:** Verifying password hashing and token creation logic.
    *   **`crud.py`:** Testing data transformation logic, such as the calculation of a cluster's `ttl_expires_at` timestamp.
    *   **`provisioner.py`:** Testing the data encryption and decryption functions. The `subprocess` calls will be mocked to verify that the correct KinD commands would be executed without actually running them.

*   **Integration Tests:** These tests will verify the interaction between different parts of the backend. They will use FastAPI's `TestClient` to make live HTTP requests to the API endpoints. A separate, temporary test database will be used to ensure test isolation and prevent corruption of development data. Scenarios will include:
    *   The full user lifecycle: Register, login, and fetch user details.
    *   The full cluster CRUD lifecycle, verifying that API calls correctly create, list, and update records in the test database.
    *   Testing failure conditions, such as attempting to create a cluster with a duplicate name, and asserting that the correct HTTP status codes and error details are returned.

#### **6.2. Frontend Testing (`Jest` & `React Testing Library`)**

The frontend will be tested to ensure that UI components render correctly and that user interactions trigger the expected behavior.

*   **Frameworks:** `Jest` will be used as the test runner, and `React Testing Library` will be used to render components and simulate user events.
*   **Component Tests:** Individual React components will be tested to verify they render correctly based on their props. Key components to test include:
    *   The cluster creation form, to check for proper input handling and button disabled states.
    *   The cluster list rendering, to ensure it correctly maps cluster data to UI elements.
    *   The `DashboardLayout`, to verify that it correctly displays user information and that the logout button functions as expected.
*   **State & Logic Tests:** The Redux Toolkit slices will be tested to ensure that actions, such as those dispatched upon receiving a WebSocket message, update the application state correctly.

#### **6.3. End-to-End (E2E) Testing (`Playwright`)**

E2E tests provide the highest level of confidence by simulating a complete user journey through the entire application stack.

*   **Framework:** `Playwright` will be used to write automated browser tests that interact with the application just as a real user would.
*   **Critical Test Scenario:** A primary E2E test script will be developed to validate the core functionality of the system from start to finish:
    1.  Navigate to the registration page and create a new user.
    2.  Log in with the new user's credentials.
    3.  On the dashboard, create a new cluster.
    4.  The test will wait and assert that the cluster's status badge updates to `RUNNING`, confirming that the backend background task and WebSocket notification system are working correctly together.
    5.  The test will then delete the cluster.
    6.  It will assert that the cluster is removed from the list in the UI, again validating the real-time update mechanism.
    7.  Finally, the test will log the user out.

### **7. Security**

Security is a foundational aspect of the PyK8s-Lab design. The V1.0 architecture builds upon the secure base of the prototype and introduces formal authorization policies.

#### **7.1. Authentication and Authorization**

*   **Authentication (Current State):** The prototype implements a robust JWT-based authentication system.
    *   **Password Hashing:** User passwords are not stored in plaintext. They are hashed using `passlib` with the `bcrypt` algorithm before being saved to the database.
    *   **Token-Based Sessions:** Upon successful login via the `POST /auth/token` endpoint, a signed JWT is issued to the client. This token must be included as a `Bearer` token in the `Authorization` header of all subsequent requests to protected endpoints.
    *   **Endpoint Protection:** FastAPI dependencies like `get_current_user` are used to ensure that only authenticated users can access protected resources.

*   **Authorization (V1.0 Plan):** With the introduction of teams, a Role-Based Access Control (RBAC) model will be implemented.
    *   **Roles:** Initially, two roles will be defined within a team: `admin` and `member`.
    *   **Permissions:** Admins will have permission to manage team members (invite, remove) and delete team-owned clusters. Members will be able to view team resources and create new resources under the team's context.
    *   **Enforcement:** API endpoints related to team management will be protected by new FastAPI dependencies that check the user's role in the `team_memberships` table. For example, a request to `POST /teams/{team_id}/members` will be rejected with a `403 Forbidden` error if the authenticated user does not have the `admin` role for that specific team.

#### **7.2. Secrets Management**

Proper management of sensitive data like encryption keys and database credentials is a critical security requirement.

*   **Current State (Prototype):** The prototype manages secrets, such as the `SECRET_KEY` for JWTs and the `ENCRYPTION_KEY` for kubeconfigs, through environment variables loaded from a `.env` file. The `provisioner.py` module uses Fernet (symmetric encryption) from the `cryptography` library to encrypt kubeconfig files before they are stored in the database. This approach is sufficient for development but must be enhanced for production.

*   **Production Recommendation (V1.0 Plan):** For a production deployment, secrets must be externalized from the application's environment.
    *   **Solution:** A dedicated secrets management tool such as **HashiCorp Vault** or a cloud-native solution (e.g., AWS Secrets Manager, GCP Secret Manager, Azure Key Vault) is strongly recommended.
    *   **Integration:** In a Kubernetes deployment, the application pods would be granted a specific identity (a Kubernetes Service Account). This identity would be authorized to retrieve secrets directly from the secret manager at runtime. This practice ensures that sensitive credentials are never hardcoded, stored in Git, or exposed as plain environment variables in the container definition.
