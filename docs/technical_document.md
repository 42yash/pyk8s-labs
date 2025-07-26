Technical Design Document: PyK8s-Lab
Version: 1.0 Date: 2025-07-24 Status: In-Progress
1. EXECUTIVE SUMMARY & PROJECT OVERVIEW
1.1 Project Purpose, Goals, and Business Value
PyK8s-Lab is a self-service, on-demand Kubernetes playground designed to provide developers, students, and DevOps engineers with ephemeral, isolated Kubernetes clusters. The primary goal is to accelerate learning, experimentation, and testing of cloud-native applications by removing the overhead associated with manual cluster setup and teardown.
Business Value:
• Increased Developer Productivity: Eliminates time spent on local environment configuration and provides a standardized, shareable platform for collaboration.
• Reduced Infrastructure Costs: Ephemeral, resource-constrained clusters with automated TTLs prevent resource wastage from long-running, unused development clusters.
• Accelerated Onboarding: New team members can get a working Kubernetes environment in minutes, not hours or days.
• Improved CI/CD Pipelines: Provides a mechanism to dynamically provision clean test environments for every pull request, leading to more reliable and isolated testing.
1.2 Key Features and Capabilities Summary
• On-Demand Cluster Provisioning: Users can create Kubernetes clusters (KinD, MicroK8s, k3s) via a web UI, mobile/desktop app, or CLI.
• Ephemeral Environments: All clusters have a configurable Time-to-Live (TTL) to ensure automatic cleanup.
• Multi-Provider Support: Flexibility to choose the underlying Kubernetes distribution that best fits the use case.
• Pre-installed Tooling: Option to bootstrap clusters with common tools like Helm, Prometheus, or popular CNABs.
• Interactive Terminal: A web-based terminal providing direct kubectl access to the provisioned cluster.
• Comprehensive CLI: A powerful CLI client for power users and CI/CD integration.
• User and Team Management: Support for individual users and teams with shared resources and quotas.
• Real-time Notifications: UI and client updates via WebSockets for cluster status changes.
1.3 Target Audience and Use Cases
• Developers: Quickly spin up a cluster to test an application, experiment with a new Kubernetes feature, or debug a production issue in an isolated environment.
• Students & Learners: An accessible, zero-cost (or low-cost) way to learn Kubernetes concepts without complex local setup.
• DevOps & SREs: A tool for testing infrastructure changes, validating Helm charts, or creating temporary environments for incident response drills.
• CI/CD Systems: Programmatically create and destroy isolated test environments for integration and end-to-end testing pipelines.
1.4 Technology Stack Overview
Component
	
Technology
	
Version(s)
Backend
	
Python, FastAPI, gRPC
	
3.11+
Frontend (Web)
	
TypeScript, React, Next.js
	
14+
Frontend (Mobile/Desktop)
	
Dart, Flutter
	
3.22+
Database
	
PostgreSQL
	
16+
Cache
	
Redis
	
7.2+
Container Runtime
	
Docker, LXD
	
26.0+, 5.21+
K8s Distributions
	
KinD, MicroK8s, k3s
	
v0.23+, 1.28+, v1.28+
CLI Client
	
Python, Click, Rich
	
3.11+, 8.1+, 13.7+
Deployment
	
Kubernetes, Helm
	
1.28+, 3.15+
Packaging
	
Docker, Snap
	
-
1.5 Success Metrics and KPIs
Metric
	
KPI Target
User Adoption
	
500+ active weekly users within 6 months.
Cluster Creation Velocity
	
P95 for cluster readiness < 120 seconds.
System Uptime
	
99.9% availability for the core API.
Resource Efficiency
	
< 5% of clusters exceeding their TTL.
CI/CD Integration Rate
	
20+ CI pipelines actively using the service.
User Satisfaction (NPS)
	
> 40
2. SYSTEM ARCHITECTURE
2.1 High-level Architecture Diagram Description
The PyK8s-Lab system is designed as a distributed, microservices-based architecture. A central API gateway routes requests from various clients (Web UI, Flutter App, CLI) to the appropriate backend services. The core logic is split between a REST API service for synchronous user-facing operations and a gRPC-based worker service for asynchronous, long-running tasks like cluster provisioning. A PostgreSQL database stores state, while Redis is used for caching and as a message broker for real-time updates.
(Description of a conceptual diagram. In a real document, this would be an actual image.)

graph TD
    subgraph Clients
        A[Web UI - React/Next.js]
        B[Mobile/Desktop - Flutter]
        C[CLI Client - Python/Click]
    end

    subgraph "Backend Infrastructure (Kubernetes)"
        D[API Gateway / Ingress]
        E[FastAPI REST API Service]
        F[gRPC Cluster Manager Service]
        G[WebSocket Service]
        H[PostgreSQL Database]
        I[Redis Cache & Pub/Sub]
        J[Provisioning Workers]
    end

    subgraph "Cluster Host Nodes"
        K[Docker/LXD]
        L[KinD Clusters]
        M[MicroK8s/k3s Clusters]
    end

    A -- HTTPS/REST --> D
    B -- HTTPS/REST & gRPC --> D
    C -- HTTPS/REST & gRPC --> D

    D -- Route --> E
    D -- Route --> F
    D -- Route --> G

    E -- CRUD Ops --> H
    E -- Cache --> I
    E -- Publishes Events --> I

    G -- Subscribes --> I
    A -- WebSocket --> G
    B -- WebSocket --> G

    E -- Schedules Task --> F
    F -- Executes --> J
    J -- Creates/Manages --> L & M
    K -- Hosts --> L & M

2.2 Component Interaction Flow
A typical user flow for creating a cluster:
1. Request Initiation: A user initiates a "Create Cluster" request from the React UI, Flutter app, or CLI client.
2. API Gateway: The request, a JWT-authenticated POST /api/v1/clusters, hits the main Ingress/API Gateway.
3. REST API Service: The request is routed to the FastAPI service. It validates the user's request and permissions (e.g., quota checks).
4. Database Write: A new Cluster record is created in the PostgreSQL database with a PROVISIONING status.
5. Task Delegation: The FastAPI service delegates the long-running provisioning task to the gRPC Cluster Manager service via a unary gRPC call.
6. Provisioning Worker: The Cluster Manager service picks a host node and instructs a provisioning worker to create the cluster using the specified provider (e.g., kind create cluster...).
7. Status Updates: The worker continuously updates the cluster status in the database and publishes status change events (e.g., PROVISIONING, RUNNING, ERROR) to a Redis Pub/Sub channel.
8. WebSocket Notification: The WebSocket service, subscribed to the Redis channel, pushes the status update to the connected client(s) for that user.
9. Client UI Update: The UI receives the WebSocket event and updates the cluster status in real-time without needing to poll the API.
2.3 Microservices Architecture Details
• FastAPI REST API (api-service): The primary user-facing service. Handles synchronous operations: authentication, user management, team management, billing/quota information, and initiating cluster operations. It is stateless and can be scaled horizontally.
• gRPC Cluster Manager (cluster-manager): Handles the core, long-running business logic of provisioning, terminating, and managing the lifecycle of Kubernetes clusters. It exposes a gRPC interface for internal communication, ensuring high-performance, strongly-typed contracts.
• WebSocket Service (websocket-service): Manages persistent WebSocket connections with clients. It subscribes to Redis Pub/Sub channels to receive real-time events from other services and broadcasts them to relevant users.
• Provisioning Workers (provisioning-worker): Lightweight, ephemeral jobs or pods that execute the actual kind, microk8s, or k3s commands on designated host nodes. This isolates the core services from the underlying container runtimes and system dependencies.
2.4 Data Flow and Communication Patterns
• Client-Backend: Clients primarily use HTTPS/REST for standard state-changing operations. WebSockets are used for receiving real-time updates. The CLI and Flutter clients may use gRPC for performance-critical queries.
• Inter-Service (Synchronous): While direct synchronous calls are minimized, the api-service uses a unary gRPC call to the cluster-manager to schedule tasks. This benefits from Protobuf's strong typing and performance.
• Inter-Service (Asynchronous): The primary pattern is Event-Driven Choreography via Redis Pub/Sub. Services publish events (e.g., cluster.created) without knowledge of the consumers. This decouples services and improves resilience.
2.5 Scalability and Performance Considerations
• Horizontal Scaling: All core backend services (api-service, cluster-manager, websocket-service) are designed to be stateless and can be scaled horizontally using Kubernetes Deployments and HPAs (Horizontal Pod Autoscalers).
• Database Scaling: The initial design uses a primary PostgreSQL instance. For future scale, read replicas will be introduced to offload read-heavy queries.
• Asynchronous Processing: Heavy lifting (cluster creation/deletion) is handled asynchronously by workers, ensuring the API remains responsive under load.
• Connection Pooling: Database and Redis connections will be managed with robust pooling libraries (e.g., asyncpg's built-in pool, redis-py's connection pool) to minimize connection overhead.
• Caching: Redis is used extensively to cache frequently accessed, semi-static data like user profiles, permissions, and service configurations, reducing database load.
2.6 Technology Stack Justification
• Python/FastAPI: Chosen for its high performance, asynchronous capabilities (built on Starlette and Uvicorn), and excellent developer experience with automatic data validation (Pydantic) and API documentation (OpenAPI).
• gRPC: Selected for high-performance internal communication between services. Its use of Protocol Buffers ensures efficient serialization and a strongly-typed, backwards-compatible API contract.
• React/Next.js: Next.js provides a powerful framework for building modern React applications, with features like server-side rendering (SSR) for fast initial page loads and a robust ecosystem.
• Flutter: Enables the creation of a single codebase for high-performance mobile (iOS/Android) and desktop (Windows/macOS/Linux) clients, maximizing code reuse.
• PostgreSQL: A mature, reliable, and feature-rich open-source relational database that supports complex queries, JSONB for flexible data, and has strong community support.
• KinD / MicroK8s / k3s: Offering multiple providers gives users flexibility. KinD is ideal for CI, MicroK8s for a full-featured experience, and k3s for a lightweight option.
3. TECHNICAL SPECIFICATIONS
3.1 Backend Services
3.1.1 FastAPI REST API complete specification
The REST API is the primary entry point for users. It is responsible for user management, authentication, and initiating cluster operations.
• Framework: FastAPI with Pydantic for data models.
• Authentication: JWT Bearer tokens, obtained via an OAuth2 flow (e.g., with Auth0, Keycloak, or a built-in provider).
• Key Namespaces:
    ◦ /users: User registration, profile management.
    ◦ /auth: Token generation and validation.
    ◦ /clusters: CRUD operations for Kubernetes clusters.
    ◦ /teams: Team and membership management.
    ◦ /providers: Listing available cluster types and versions.
3.1.2 gRPC service definitions and protocol buffers
The ClusterManager service handles the core logic for cluster lifecycle.
• Protocol: gRPC with Protocol Buffers v3.
• Key Services & Methods:
    ◦ ClusterService:
        ▪ CreateCluster(CreateClusterRequest) returns (ClusterResponse): Initiates cluster creation.
        ▪ TerminateCluster(TerminateClusterRequest) returns (google.protobuf.Empty): Schedules a cluster for termination.
        ▪ GetClusterStatus(GetClusterStatusRequest) returns (ClusterStatusResponse): Retrieves the detailed status of a cluster.
        ▪ StreamClusterLogs(StreamClusterLogsRequest) returns (stream LogEntry): Streams provisioning logs.
3.1.3 WebSocket implementations for real-time features
A dedicated WebSocket service manages persistent connections for real-time UI updates.
• Path: /ws/v1/{user_id}
• Authentication: The connection request includes a short-lived JWT passed as a query parameter. The server validates this token before upgrading the connection.
• Message Format: JSON objects with event and payload fields.
    ◦ Example: {"event": "cluster.status.changed", "payload": {"cluster_id": "...", "status": "RUNNING"}}
3.1.4 Authentication and authorization mechanisms
• Authentication: OAuth 2.0 Authorization Code Flow for web clients. The backend issues a stateless JWT containing user_id, team_id, roles, and an expiration claim (exp).
• Authorization: Role-Based Access Control (RBAC). Permissions are defined for roles (e.g., user, team_admin, global_admin) and checked within API endpoints using FastAPI dependencies.
3.1.5 Database schema and data models
• ORM: SQLAlchemy 2.0 with its asyncio extension.
• Key Tables:
    ◦ users: Stores user information, credentials hash, and profile data.
    ◦ teams: Defines teams of users.
    ◦ team_memberships: Maps users to teams with roles.
    ◦ clusters: The central table storing cluster configuration, owner, status, TTL, provider type, and kubeconfig.
    ◦ audit_log: Records significant events for security and debugging.
3.1.6 Caching strategy (Redis integration)
Redis serves multiple purposes:
• Session/Data Caching: Caching user permissions and frequently accessed data to reduce DB load.
• Rate Limiting: Storing request counts per user/IP for API rate limiting.
• Pub/Sub Broker: Decoupling services by acting as a real-time event bus for status updates.
3.2 Container Orchestration Engine
3.2.1 Kubernetes cluster provisioning logic
1. API receives a request and creates a DB entry.
2. gRPC service receives the task.
3. A provisioning worker is dispatched to a host node with sufficient capacity.
4. The worker generates a unique cluster name and configuration file.
5. It executes the provider-specific command (e.g., kind create cluster --config ...).
6. Upon success, it retrieves the kubeconfig, encrypts it, and stores it in the clusters table.
7. The worker updates the cluster status to RUNNING and publishes a success event.
3.2.2 KinD, MicroK8s, and k3s integration details
• KinD: Used with the Docker provider. The worker runs kind commands directly. Cluster configuration is passed via a YAML file.
• MicroK8s: Installed on host nodes as a Snap. The worker uses microk8s launch or multipass to spin up isolated VM-based clusters. Addons are enabled via microk8s enable ....
• k3s: Can be deployed via k3s-root scripts or the k3d wrapper for a Docker-based experience similar to KinD.
3.2.3 Container runtime abstractions (Docker, LXD)
The cluster-manager service includes an abstraction layer to interact with different host-level runtimes. This allows for flexible scheduling of cluster workloads on nodes running either Docker (for KinD) or LXD (for full system container isolation, potentially with MicroK8s).
3.2.4 Resource management and TTL mechanisms
• TTL: Every cluster is created with a ttl_expires_at timestamp in the database. A background cron job periodically scans for expired clusters and queues them for termination. Users can request a TTL extension via the API.
• Quotas: User and team-level quotas (e.g., max active clusters, max CPU/memory allocation) are defined in the database and enforced by the api-service before provisioning.
3.2.5 Multi-tenancy implementation
• Data Plane Isolation: Each user's cluster is a completely separate instance of KinD/MicroK8s/k3s, running in its own set of containers or a dedicated VM. There is no shared Kubernetes control plane between tenants.
• Control Plane Isolation: All API requests are authenticated and authorized, ensuring a user can only see and manage their own resources (clusters, teams).
3.2.6 Cluster lifecycle management
The system manages the full lifecycle:
• Create: POST /api/v1/clusters -> gRPC CreateCluster
• Read/Get: GET /api/v1/clusters/{id}
• List: GET /api/v1/clusters
• Delete/Terminate: DELETE /api/v1/clusters/{id} -> gRPC TerminateCluster
• Extend TTL: POST /api/v1/clusters/{id}/extend
3.3 Frontend Applications
3.3.1 React/Next.js web dashboard architecture
• Framework: Next.js 14 with App Router.
• State Management: Redux Toolkit for centralized state and RTK Query for data fetching and caching, integrated with the REST API.
• Styling: Material-UI (MUI) for a pre-built component library, styled with CSS-in-JS.
• Key Directories:
    ◦ /app: Contains page routes.
    ◦ /components: Reusable UI components.
    ◦ /lib: Utility functions, API clients.
    ◦ /store: Redux Toolkit setup.
3.3.2 Flutter mobile/desktop client specifications
• Architecture: BLoC (Business Logic Component) pattern for separating UI from business logic.
• State Management: flutter_bloc library.
• API Communication: http package for REST, grpc package for gRPC, and web_socket_channel for WebSockets.
• Code Structure: Feature-driven directory structure (e.g., /lib/clusters, /lib/auth).
3.3.3 Real-time UI updates via WebSocket
The WebSocket client connects upon user login, authenticates, and listens for events. A central event handler maps incoming events (e.g., cluster.status.changed) to Redux actions, which update the state and cause the relevant UI components to re-render automatically.
3.3.4 State management and data flow
State is managed optimistically where possible. For example, when creating a cluster, the UI immediately shows a "provisioning" state and relies on WebSocket events for updates, rather than polling the API. RTK Query handles server-side state, caching, and invalidation automatically.
3.3.5 Component library and design system
A custom design system will be built on top of MUI for React and Material 3 for Flutter, ensuring brand consistency. Reusable components (e.g., ClusterCard, StatusIndicator, ResourceGauge) will be documented in Storybook (for React) and a widget catalog (for Flutter).
3.3.6 Responsive design requirements
The web application must be fully responsive and functional across three primary breakpoints:
• Mobile: < 600px
• Tablet: 600px - 960px
• Desktop: > 960px Flexbox and CSS Grid will be used extensively.
3.4 CLI Client
3.4.1 Click-based command structure
The CLI uses click to create a nested command structure.
• Root command: pyk8s
• Groups: pyk8s cluster, pyk8s auth, pyk8s team
• Commands:
    ◦ pyk8s cluster create --name my-cluster --provider kind
    ◦ pyk8s cluster list
    ◦ pyk8s cluster delete my-cluster
    ◦ pyk8s cluster get-kubeconfig my-cluster > kubeconfig.yaml
    ◦ pyk8s auth login
3.4.2 API client integration
The CLI uses a generated API client (or a manually crafted one using httpx) to communicate with the REST API. It manages JWTs by storing them securely in a local configuration file.
3.4.3 Rich terminal interface specifications
The rich library is used to provide:
• Formatted tables for list commands.
• Color-coded output and status indicators.
• Progress spinners for long-running operations.
• Syntax-highlighted output for YAML/JSON.
3.4.4 Configuration management
• Location: ~/.config/pyk8s-lab/config.yaml
• Contents: API server URL, active user, stored refresh token.
• Security: File permissions are set to 600 to protect sensitive contents.
3.4.5 Error handling and user feedback
API errors (4xx/5xx) are caught and translated into user-friendly messages. Validation errors from the server are displayed clearly, indicating the incorrect parameter. The --verbose flag provides full stack traces for debugging.
4. API DOCUMENTATION
4.1 REST API Specification
4.1.1 Complete OpenAPI/Swagger specification
The FastAPI backend auto-generates an OpenAPI 3.0 specification available at /openapi.json and a Swagger UI at /docs.
• Sample OpenAPI Snippet for POST /clusters:
4.1.2 All endpoints with request/response schemas
All API endpoints and their Pydantic-based schemas will be fully documented via the auto-generated OpenAPI spec.
4.1.3 Authentication flows and security headers
• Authentication: Authorization: Bearer <JWT> header is required for all protected endpoints.
• Flow: Clients obtain the JWT via the /auth/token endpoint as part of an OAuth2 flow.
4.1.4 Rate limiting and quota management
• Headers: Successful responses may include the following headers:
    ◦ X-RateLimit-Limit: The request quota for the current window.
    ◦ X-RateLimit-Remaining: The number of requests remaining in the window.
    ◦ X-RateLimit-Reset: The UTC epoch seconds when the quota resets.
• Response: A 429 Too Many Requests status code is returned when the limit is exceeded.
4.1.5 Error codes and handling
• 400 Bad Request: Validation error. Response body contains details.
• 401 Unauthorized: Invalid or missing authentication token.
• 403 Forbidden: User is authenticated but not permitted to perform the action.
• 404 Not Found: The requested resource does not exist.
• 500 Internal Server Error: A generic server error.
4.2 gRPC Service Definition
4.2.1 Complete Protocol Buffer definitions
• File: cluster_manager.proto
4.2.2 Service methods and message types
The .proto file serves as the definitive source for all service methods and their associated message structures.
4.2.3 Streaming implementations
• StreamClusterLogs: A server-side streaming RPC. The client makes a single request, and the server streams back log messages as they are generated during the provisioning process. This is ideal for providing real-time feedback in the UI or CLI.
4.2.4 Error handling and status codes
gRPC errors are handled using standard gRPC status codes.
• INVALID_ARGUMENT: Bad input in the request message.
• NOT_FOUND: The specified cluster ID does not exist.
• RESOURCE_EXHAUSTED: The system has no capacity to provision a new cluster.
• INTERNAL: An unhandled exception occurred in the service.
4.2.5 Load balancing considerations
When the cluster-manager service is scaled to multiple replicas, a gRPC-aware load balancer (like Linkerd, Istio, or a dedicated gRPC proxy) should be used. Client-side load balancing (e.g., pick_first or round_robin) can be configured in the gRPC clients.
4.3 WebSocket API
4.3.1 Real-time event specifications
• cluster.status.changed: Sent when a cluster's status changes (e.g., PROVISIONING -> RUNNING).
• cluster.ttl.extended: Sent when a cluster's TTL is successfully updated.
• terminal.data.received: For the interactive terminal, streams data from the cluster's TTY.
• notification.user.info: General notifications for the user.
4.3.2 Message formats and protocols
• Format: JSON
• Structure:
4.3.3 Connection management
Clients are expected to handle connection drops and implement an exponential backoff retry strategy. The server will periodically send ping frames, and clients should respond with pong frames to keep the connection alive through proxies and load balancers.
4.3.4 Authentication over WebSocket
A short-lived, single-use JWT is passed as a query parameter during the initial HTTP connection request before the upgrade to WebSocket. Example: wss://api.pyk8s-lab.io/ws/v1/me?token=.... The server validates the token and binds the connection to the authenticated user ID.
5. DATABASE DESIGN
The persistence layer for PyK8s-Lab is built upon PostgreSQL 16+, chosen for its reliability, feature set (including robust JSONB support), and performance. The primary ORM used in the backend services is SQLAlchemy 2.0 with its asyncio extension.
5.1 Complete Entity-Relationship Diagrams
(Description of a conceptual ERD. In a real document, this would be an actual image.)
The database schema is centered around users and their clusters. A user can belong to multiple teams through a team_memberships join table, which also defines their role within that team. Each cluster is owned by a single user and is optionally associated with a team. An audit_log table tracks significant actions performed on these entities for security and traceability.

erDiagram
    users {
        UUID id PK
        String email UK
        String hashed_password
        String full_name
        Timestamptz created_at
        Timestamptz updated_at
    }

    teams {
        UUID id PK
        String name UK
        String description
        Timestamptz created_at
        Timestamptz updated_at
    }

    team_memberships {
        UUID user_id PK, FK
        UUID team_id PK, FK
        String role "e.g., 'admin', 'member'"
        Timestamptz joined_at
    }

    clusters {
        UUID id PK
        String name
        String status
        String provider
        JSONB provider_config
        TEXT encrypted_kubeconfig
        Timestamptz ttl_expires_at
        Timestamptz created_at
        Timestamptz updated_at
        UUID user_id FK
        UUID team_id FK "nullable"
    }

    audit_log {
        UUID id PK
        UUID user_id FK
        String action
        JSONB details
        Timestamptz created_at
    }

    users ||--o{ team_memberships : "has"
    teams ||--o{ team_memberships : "has"
    users ||--o{ clusters : "owns"
    teams ||--o{ clusters : "owns"
    users ||--o{ audit_log : "performs"

5.2 Table Schemas with Constraints
Below are the simplified SQL CREATE TABLE statements representing the core schemas.

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL, -- e.g., 'PROVISIONING', 'RUNNING', 'TERMINATING', 'ERROR'
    provider VARCHAR(50) NOT NULL, -- e.g., 'kind', 'microk8s', 'k3s'
    provider_config JSONB,
    encrypted_kubeconfig TEXT,
    ttl_expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name) -- A user cannot have two clusters with the same name
);

-- Other tables like 'teams', 'team_memberships', 'audit_log' follow a similar structure.

5.3 Indexing Strategy
To ensure performant queries, the following indexes will be created:
• Primary Keys: Automatically indexed.
• Foreign Keys: Indexes will be created on all foreign key columns (clusters.user_id, clusters.team_id, etc.) to speed up joins.
• Frequently Queried Columns:
    ◦ users(email): For fast login lookups.
    ◦ clusters(status): To quickly find all clusters in a specific state (e.g., for the TTL cleanup worker).
    ◦ clusters(ttl_expires_at): For the TTL cleanup worker.
• GIN Index for JSONB: A GIN index will be placed on clusters.provider_config to allow for fast lookups inside the JSONB data structure if needed.
5.4 Migration Scripts Structure
Database schema migrations will be managed using Alembic.
• Directory Structure: A standard Alembic project structure will be maintained in the api-service repository under /alembic.
• Workflow:
    1. Modify SQLAlchemy models in the application code.
    2. Run alembic revision --autogenerate -m "Description of changes" to create a new migration script.
    3. Review and refine the auto-generated script.
    4. Apply migrations during deployment using alembic upgrade head.
5.5 Backup and Recovery Procedures
• Backup: Point-in-Time Recovery (PITR) will be configured for the PostgreSQL database. This involves continuous archiving of WAL (Write-Ahead Log) files to an object store (e.g., S3, GCS). A full base backup will be taken nightly.
• Recovery:
    ◦ Recovery Point Objective (RPO): 5 minutes.
    ◦ Recovery Time Objective (RTO): 1 hour.
    ◦ Procedure: A documented runbook will detail the steps to restore the database from the base backup and WAL archives to a specific point in time. This procedure will be tested quarterly.
5.6 Performance Optimization
• Connection Pooling: The FastAPI service will use asyncpg's built-in connection pool to efficiently manage and reuse database connections.
• Query Analysis: EXPLAIN ANALYZE will be used to inspect and optimize slow-running queries during development.
• Read Replicas: For future scaling, the application architecture will support routing read-only queries to a PostgreSQL read replica to reduce load on the primary instance.
6. SECURITY ARCHITECTURE
6.1 Authentication Mechanisms (JWT, OAuth2)
• Standard: OAuth 2.0 and OpenID Connect (OIDC).
• Flow: The primary flow for web clients is the Authorization Code Flow with PKCE.
    1. The frontend redirects the user to an identity provider (e.g., Keycloak, Auth0, Google).
    2. After successful login, the user is redirected back with an authorization code.
    3. The frontend sends this code to the backend's /auth/token endpoint.
    4. The backend verifies the code with the identity provider and receives an id_token and access_token. It then issues its own internal, stateless JWT to the client.
• JWT Structure: The internal JWT will contain standard claims (iss, sub, exp, aud) as well as custom claims like user_id, team_id, and roles.
6.2 Authorization and RBAC Implementation
• Model: A Role-Based Access Control (RBAC) model is implemented.
    ◦ Roles: user, team_admin, system_admin.
    ◦ Permissions: Granular permissions are associated with each role (e.g., cluster:create, cluster:delete, team:invite_member).
• Enforcement: Enforcement is handled in the FastAPI backend using dependencies. A dependency will decode the JWT, fetch the user's roles and permissions (potentially from a cache), and verify if the requested action is permitted.
6.3 API Security Best Practices
• Transport Security: TLS 1.3 is enforced for all external communication.
• Input Validation: Pydantic models provide strict input validation, preventing mass assignment vulnerabilities and common injection attacks.
• Security Headers: The API will set security headers like Content-Security-Policy, Strict-Transport-Security, and X-Content-Type-Options.
• CORS: A strict Cross-Origin Resource Sharing (CORS) policy will be configured to only allow requests from known frontend domains.
6.4 Container and Cluster Isolation
• Core Principle: Zero-trust, maximum isolation.
• Tenant Cluster Isolation: Each tenant's Kubernetes cluster is provisioned as a distinct entity (e.g., a set of Docker containers for KinD, a separate VM for MicroK8s). There is no shared kernel or control plane between tenant clusters.
• Network Policies: On the host nodes where clusters are provisioned, iptables or nftables rules will be configured to prevent tenant clusters from communicating with each other or with the host's metadata services. Each KinD cluster's container network is inherently isolated by Docker.
6.5 Network Security Policies
Within the main Kubernetes cluster where PyK8s-Lab itself is deployed:
• Default Deny: A default NetworkPolicy will be in place to deny all pod-to-pod traffic.
• Explicit Allow: Policies will be created to explicitly allow required communication paths (e.g., api-service can talk to postgresql and redis on their specific ports).
• Ingress/Egress Control: Egress traffic from the cluster will be restricted to only necessary external endpoints (e.g., identity providers, image registries).
6.6 Secrets Management
• Solution: HashiCorp Vault or a cloud provider's native secret manager (e.g., AWS Secrets Manager, GCP Secret Manager).
• Mechanism: The application pods will be associated with a Kubernetes Service Account that has permission to retrieve secrets from Vault. The Vault Agent sidecar injector will be used to automatically fetch secrets and mount them as files into the application pods.
• Secrets: This includes database credentials, API keys for external services, and the private key used for encrypting kubeconfig data at rest. kubeconfig files stored in the database are encrypted using Fernet symmetric encryption before being persisted.
6.7 Compliance Considerations
• GDPR/CCPA: The system will be designed with data privacy in mind. Features will include the ability for users to request and export their data, as well as a clear process for account deletion which purges all associated personal information and resources.
• SOC 2: The audit_log table is a foundational element for achieving SOC 2 compliance, providing a trail of significant user and system actions.
7. DEPLOYMENT & INFRASTRUCTURE
7.1 Kubernetes Deployment
The entire PyK8s-Lab platform is deployed as a set of microservices on a dedicated Kubernetes cluster. Helm is the standard for packaging and deployment.
7.1.1 Complete Helm chart specifications
A parent Helm chart (pyk8s-lab) will manage several sub-charts:
• api-service
• cluster-manager
• websocket-service
• Dependencies like postgresql and redis (which can be toggled off to use managed cloud services).
values.yaml (Template):

# values.yaml
global:
  imageRegistry: "ghcr.io/pyk8s-lab"
  imagePullPolicy: IfNotPresent
  pyk8sLabVersion: "1.0.0"

apiService:
  replicaCount: 2
  image:
    tag: "1.0.0"
  resources:
    requests:
      cpu: "250m"
      memory: "256Mi"
    limits:
      cpu: "1000m"
      memory: "512Mi"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80

# ... similar sections for cluster-manager, websocket-service

postgresql:
  enabled: true # Set to false if using an external DB
  auth:
    username: "pyk8sadmin"
    database: "pyk8slab_db"
    # Password will be sourced from a Kubernetes secret```

#### 7.1.2 Resource requirements and limits
Defined in the Helm chart as shown above. These values will be tuned based on load testing.

#### 7.1.3 ConfigMaps and Secrets management
*   **ConfigMaps:** Used for non-sensitive configuration like API URLs, log levels, and feature flags.
*   **Secrets:** Used for all sensitive data. Secrets will be created declaratively and managed by ArgoCD or a similar GitOps tool. For production, they will be populated by an external secret store integration like the Vault Agent Injector.

#### 7.1.4 Service mesh integration (if applicable)
**Linkerd** is the recommended service mesh due to its simplicity, performance, and transparent mTLS.
*   **Integration:** The Helm chart will include annotations (`linkerd.io/inject: enabled`) to automatically inject the Linkerd proxy sidecar into application pods.
*   **Benefits:**
    *   Automatic mTLS for all inter-service communication.
    *   L7 load balancing for gRPC.
    *   Golden metrics (success rate, requests/sec, latency) for all services out-of-the-box.

#### 7.1.5 Ingress and load balancer configuration
*   **Ingress Controller:** NGINX Ingress Controller.
*   **Configuration:** The Helm chart will create `Ingress` resources to route external traffic.
    *   `api.pyk8s-lab.io/api` -> `api-service`
    *   `api.pyk8s-lab.io/ws` -> `websocket-service`
    *   gRPC traffic can be routed via the same Ingress on a separate path or hostname with appropriate configuration.

### 7.2 Container Packaging

#### 7.2.1 Dockerfile specifications for all components
A multi-stage Dockerfile will be used for each service to create lean, secure production images.

**Example `Dockerfile` for `api-service`:**
```dockerfile
# Stage 1: Build stage with all dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency files and install only dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-dev

# Stage 2: Final production image
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy virtual env from builder stage
COPY --from=builder /app/.venv /.venv

# Copy application code
COPY . .

# Activate venv and set user
ENV PATH="/app/.venv/bin:$PATH"
USER app

# Command to run the application
CMD ["uvicorn", "pyk8s_lab.main:app", "--host", "0.0.0.0", "--port", "8000"]

7.2.2 Multi-stage build optimization
As shown above, this practice separates build-time dependencies from the final runtime image, significantly reducing its size and attack surface.
7.2.3 Security scanning integration
Container images will be scanned for vulnerabilities as part of the CI/CD pipeline using a tool like Trivy or Snyk. A high-severity vulnerability finding will fail the build.
7.2.4 Image registry and versioning strategy
• Registry: A private container registry (e.g., GitHub Container Registry, Docker Hub, Harbor) will be used.
• Versioning: Images will be tagged with the Git commit SHA and the semantic version number (e.g., ghcr.io/pyk8s-lab/api-service:1.2.3-a1b2c3d).
7.3 Snap Package
For distributing MicroK8s or a bundled version of the CLI, a Snap package provides easy installation and automatic updates.
7.3.1 Complete snapcraft.yaml specification
This file defines the Snap package for the pyk8s-cli.

name: pyk8s-cli
base: core22 # Use Ubuntu 22.04 LTS as the base
version: '1.0.0'
summary: CLI for the PyK8s-Lab Kubernetes Playground
description: |
  Create and manage ephemeral Kubernetes clusters for development
  and testing with PyK8s-Lab.

grade: stable
confinement: strict # Use strict confinement for security

apps:
  pyk8s:
    command: bin/pyk8s
    plugs:
      - network # Required for API access
      - home    # For accessing ~/.config/pyk8s-lab

parts:
  cli:
    plugin: python
    source: .
    python-version: python3
    requirements:
      - requirements.txt

7.3.2 Confinement and interface requirements
• Confinement: strict to ensure the application is properly isolated from the host system.
• Plugs (Interfaces): The CLI will require the network plug to communicate with the API server and the home plug (with a specific personal files interface if possible) to access its configuration file.
7.3.3 Installation and configuration steps
• Installation: sudo snap install pyk8s-cli
• Configuration: On first run, the CLI will prompt the user to log in (pyk8s auth login), which initiates the OAuth flow and saves the token to ~/snap/pyk8s-cli/current/.config/pyk8s-lab/config.yaml.
7.3.4 Auto-update mechanisms
The Snap Store automatically handles background updates. The Snap can be configured with different channels (e.g., stable, candidate, beta, edge) to manage release rollouts.
8. MONITORING & OBSERVABILITY
The monitoring stack will be built on the "three pillars of observability": metrics, logs, and traces.
8.1 Prometheus metrics specifications
All backend services will expose a /metrics endpoint in the Prometheus exposition format using a client library (e.g., prometheus-fastapi-instrumentator).
• Key Metrics:
    ◦ pyk8s_http_requests_total: Counter for total HTTP requests, with labels for service, method, path, and status_code.
    ◦ pyk8s_http_requests_duration_seconds: Histogram of request latencies.
    ◦ pyk8s_cluster_provisioning_duration_seconds: Histogram of time taken to provision clusters, labeled by provider.
    ◦ pyk8s_active_clusters_total: Gauge showing the current number of active clusters, labeled by provider and status.
    ◦ pyk8s_grpc_requests_total: Similar metrics for gRPC services.
8.2 Grafana dashboard configurations
Dashboards will be provisioned as JSON models via Grafana's provisioning feature.
• API Service Dashboard: Shows request rate, error rate, latencies (99th, 95th, 50th percentiles), and saturation metrics (CPU/memory usage).
• Cluster Manager Dashboard: Tracks the number of active clusters, provisioning success/failure rate, and provisioning duration.
• Business KPIs Dashboard: High-level metrics like user sign-ups, clusters created per day, and provider popularity.
8.3 Logging strategy and structured logs
• Format: All services will output logs as JSON. This allows for easy parsing, filtering, and indexing in a log aggregation system like Loki or the ELK stack.
• Content: Each log entry will include a timestamp, log level, service name, and a correlation ID to trace a single request across multiple services.
• Aggregation: Loki is the recommended log aggregation tool, as it integrates seamlessly with Prometheus and Grafana. Promtail will be deployed as a DaemonSet to collect logs from all pods.
8.4 Distributed tracing implementation
• Standard: OpenTelemetry will be used for distributed tracing.
• Integration:
    1. The FastAPI services will use the opentelemetry-instrumentation-fastapi library.
    2. A trace ID will be generated at the edge (API Gateway or api-service) and propagated across all subsequent gRPC and HTTP calls via headers.
• Backend: Jaeger or Tempo will be used as the tracing backend to store and visualize traces. Grafana will be configured to link from logs to traces using the shared correlation ID.
8.5 Health checks and readiness probes
Kubernetes health checks are critical for reliable, zero-downtime deployments.
• Liveness Probe: GET /health/live - A simple endpoint that returns 200 OK. If this fails, Kubernetes will restart the container.
• Readiness Probe: GET /health/ready - A more comprehensive check that verifies connectivity to the database and Redis. If this fails, the pod is removed from the service's load balancing pool until it becomes ready again. This ensures traffic is not sent to a pod that cannot serve it correctly.
8.6 Alerting rules and runbooks
• Alerting: Alertmanager will be used to manage alerts defined in Prometheus.
• Example Alerting Rules (prometheus-rules.yaml):
• Runbooks: Every alert will have a corresponding runbook in a version-controlled repository. The runbook will detail the alert's meaning, potential causes, and step-by-step diagnostic and resolution procedures.
9. TESTING STRATEGY
A multi-layered testing strategy is essential to ensure the robustness, reliability, and security of PyK8s-Lab. Each layer of testing provides a different level of feedback and confidence.
9.1 Unit Testing Framework and Coverage Targets
Unit tests focus on isolating and verifying the smallest units of code, such as individual functions or classes, in isolation from their dependencies.
• Backend & CLI (Python):
    ◦ Framework: pytest
    ◦ Libraries: pytest-mock for mocking dependencies, pytest-asyncio for testing asynchronous code.
    ◦ Coverage Target: > 85% line coverage, enforced by the CI pipeline.
• Frontend (React/Next.js):
    ◦ Framework: Jest with React Testing Library.
    ◦ Focus: Testing individual components, custom hooks, and state management logic (Redux slices).
    ◦ Coverage Target: > 80% statement coverage.
9.2 Integration Test Specifications
Integration tests verify the interactions between different components or microservices.
• Scope: These tests will run within the CI pipeline and will use docker-compose or a similar tool to spin up ephemeral instances of dependencies like PostgreSQL and Redis.
• Backend Scenarios:
    ◦ Verify that a call to the api-service's POST /clusters endpoint successfully triggers a gRPC call to the cluster-manager.
    ◦ Test the full authentication and authorization flow, ensuring RBAC rules are correctly enforced at the API layer.
    ◦ Validate that events published to Redis by one service are correctly consumed by another (e.g., the websocket-service).
• Framework: pytest will be used to orchestrate these tests, making real HTTP and gRPC calls to the services running in containers.
9.3 End-to-End (E2E) Testing Scenarios
E2E tests simulate real user workflows from the client (UI or CLI) to the backend and back again. These are run against a dedicated, fully deployed staging environment.
• Framework: Playwright for its ability to automate modern web apps across different browsers.
• Key Scenarios:
    1. User Registration & Login: A user can sign up, log in, and receive a valid JWT.
    2. Full Cluster Lifecycle (UI): A user can log into the web UI, create a kind cluster, see its status update in real-time to RUNNING, view its details, retrieve its kubeconfig, extend its TTL, and finally terminate it.
    3. Full Cluster Lifecycle (CLI): A user can perform the same lifecycle operations as above using the pyk8s CLI commands.
    4. Team Collaboration: A team admin can create a team, invite a member, and the member can see and manage team-owned clusters.
9.4 Performance and Load Testing
Performance testing ensures the system meets its defined KPIs under stress.
• Tool: k6 (Grafana k6) for its powerful scripting capabilities and developer-friendly experience.
• Test Scenarios:
    ◦ API Load Test: Simulate 500 concurrent users browsing the dashboard and making API calls.
    ◦ Stress Test: Ramp up concurrent cluster creation requests to identify the system's breaking point and maximum throughput.
    ◦ Soak Test: A long-running test (e.g., 8 hours) with moderate load to detect memory leaks or performance degradation over time.
• Metrics: P95/P99 latency, request throughput, error rate, and resource utilization will be monitored during tests.
9.5 Security Testing Requirements
Security testing is integrated directly into the development lifecycle.
• SAST (Static Application Security Testing):
    ◦ Tools: Bandit for Python, ESLint security plugins for TypeScript.
    ◦ Integration: Run automatically on every commit in the CI pipeline to find common security flaws in the source code.
• DAST (Dynamic Application Security Testing):
    ◦ Tool: OWASP ZAP (Zed Attack Proxy).
    ◦ Integration: Run automated scans against the staging environment weekly to find runtime vulnerabilities like XSS, CSRF, and insecure header configurations.
• SCA (Software Composition Analysis):
    ◦ Tool: Trivy or Snyk.
    ◦ Integration: Scans container images and third-party libraries for known CVEs as a CI pipeline step. Builds will fail if critical vulnerabilities are found.
9.6 CI/CD Pipeline Integration
The testing strategy is the backbone of the CI/CD pipeline. A pull request must pass all of the following quality gates before it can be merged:
1. Code Linting & Formatting Checks
2. SAST Scans
3. Unit Tests (with coverage check)
4. Integration Tests
5. Container Build & SCA Scan
E2E and performance tests are run on a schedule against the staging environment after successful deployments.
10. DEVELOPMENT WORKFLOW
A standardized workflow ensures consistency, quality, and predictability in the development process.
10.1 Git Branching Strategy and Workflows
• Strategy: Trunk-Based Development.
    ◦ main: The single, stable trunk. This branch is always in a releasable state.
    ◦ Feature Branches: Developers create short-lived feature branches from main (e.g., feature/TICKET-123-add-ttl-extension).
    ◦ Pull Requests (PRs): Once work is complete, a PR is opened to merge the feature branch back into main.
• Rationale: This model simplifies the branching structure and aligns perfectly with Continuous Integration and Continuous Deployment practices.
10.2 Code Review Process and Standards
• Pull Request Template: PRs must follow a template that includes a summary of changes, testing procedures, and a link to the corresponding issue tracker ticket.
• Required Checks: All automated CI checks (lint, test, scan) must pass.
• Approvals: At least one approval from another team member is required before merging. For critical components, two approvals may be enforced using branch protection rules.
• Code Style:
    ◦ Python: black for formatting, isort for import sorting, and flake8 for linting. Enforced automatically with pre-commit hooks.
    ◦ Frontend: prettier for formatting, eslint for linting.
10.3 Continuous Integration Pipeline
• Platform: GitHub Actions.
• Trigger: On every push to a feature branch and on PR creation/update against main.
• Workflow (.github/workflows/ci.yml):
    1. Checkout & Setup: Check out the code and set up the correct language versions (Python, Node.js).
    2. Lint & Format: Run linters and format checkers.
    3. Unit & Integration Tests: Install dependencies and run the pytest and jest test suites.
    4. Security Scans: Run SAST and dependency checks.
    5. Build & Scan Image: Build the Docker image and run a Trivy scan on it.
    6. Notify: Post a success or failure status back to the PR.
10.4 Automated Testing and Quality Gates
The CI pipeline acts as the primary quality gate. A PR is blocked from merging if any of the following conditions are not met:
• All CI jobs pass successfully.
• Test coverage has not decreased.
• No new "critical" or "high" vulnerabilities have been introduced.
• The required number of code review approvals has been met.
10.5 Release Management Process
• Versioning: The project follows Semantic Versioning (vMAJOR.MINOR.PATCH).
• Process:
    1. Releases are triggered manually via a GitHub Actions workflow.
    2. The workflow prompts for a version number (e.g., v1.1.0).
    3. It automatically creates a Git tag for that version on the main branch.
    4. A changelog is auto-generated from PR titles since the last release.
    5. A GitHub Release is created with the tag and changelog.
    6. The new version tag triggers a separate deployment pipeline that builds and pushes versioned container images (e.g., .../api-service:1.1.0) and Helm charts.
10.6 Documentation Maintenance
Documentation is treated as code.
• Requirement: Any PR that introduces a user-facing change or modifies an API or architecture must include corresponding updates to the documentation (READMEs, OpenAPI spec, this TDD).
• Review: Documentation changes are reviewed as part of the standard code review process.
11. OPERATIONAL PROCEDURES
This section provides Standard Operating Procedures (SOPs) for the team responsible for maintaining the PyK8s-Lab production environment.
11.1 Installation and Setup Procedures
Deploying the entire platform is managed via the parent Helm chart.
1. Prerequisites: A running Kubernetes cluster (v1.28+) with kubectl configured, Helm v3.15+, and an NGINX Ingress Controller.
2. Namespace Creation: kubectl create namespace pyk8s-lab
3. Secret Creation: Create a Secret in the pyk8s-lab namespace containing database passwords and other sensitive credentials.
4. Configuration: Customize the Helm chart's values.yaml file to configure the domain, replica counts, and external service endpoints (e.g., managed PostgreSQL).
5. Deployment: helm install pyk8s-lab ./charts/pyk8s-lab -n pyk8s-lab -f values.yaml
11.2 Configuration Management
• Methodology: GitOps using ArgoCD.
• Workflow: The desired state of the production environment (including the specific Helm chart version and values.yaml configurations) is defined in a dedicated Git repository. ArgoCD continuously monitors this repository and automatically applies any changes to the Kubernetes cluster, providing a single source of truth and an auditable history of all deployments.
11.3 Backup and Disaster Recovery
• Scenario: The primary database cluster has suffered catastrophic data loss.
• Runbook (High-Level):
    1. Declare an incident and notify stakeholders.
    2. Scale down all application deployments (api-service, etc.) to prevent further writes.
    3. Follow the cloud provider's documentation to restore the PostgreSQL database from the latest nightly backup and replay WAL files to the last known good point-in-time (RPO < 5 mins).
    4. Verify data integrity on the restored database.
    5. Scale the application deployments back up.
    6. Perform E2E tests to validate system functionality.
    7. Resolve the incident.
11.4 Scaling Procedures
• Automatic Scaling: The HorizontalPodAutoscaler (HPA) is configured for all stateless services (api-service, cluster-manager, websocket-service). It will automatically add or remove pods based on CPU utilization.
• Manual Scaling: If immediate scaling is required, an operator can manually override the replica count: kubectl scale deployment/api-service -n pyk8s-lab --replicas=5
• Database Scaling: For read-heavy workloads, add a read replica to the PostgreSQL cluster and configure the api-service to route read-only queries to it.
11.5 Troubleshooting Guides
• Symptom: API is slow or returning 5xx errors.
    1. Check Grafana: Look at the API Service dashboard. Is latency up? Is there a spike in 5xx errors? Is CPU/memory saturated?
    2. Check Logs: kubectl logs -n pyk8s-lab -l app=api-service -f --tail=100. Look for exceptions or error messages. Use the correlation ID to trace a failing request.
    3. Check Pod Status: kubectl get pods -n pyk8s-lab. Are all pods Running? Are there any restarts?
    4. Check Dependencies: Is the database or Redis experiencing issues? Check their respective dashboards.
11.6 Performance Tuning Guidelines
• API Endpoints: Use Grafana and distributed tracing to identify the slowest API endpoints.
• Database Queries: For slow endpoints, check the logs for slow database queries. Use EXPLAIN ANALYZE on these queries to check for missing indexes or inefficient join strategies.
• Resource Allocation: If pods are consistently CPU-throttled or OOMKilled, adjust the requests and limits in the Helm chart.
• Caching: For read-heavy, slow endpoints, evaluate if the response can be cached in Redis to reduce database load.
12. APPENDICES
12.1 Complete Code Examples and Snippets
CLI Command using Click and Rich:

import click
from rich.console import Console
from rich.table import Table

# (Assuming 'api_client' is an initialized client instance)

@click.command()
def list():
    """Lists all of your active clusters."""
    console = Console()
    with console.status("[bold green]Fetching clusters..."):
        try:
            clusters = api_client.get_clusters()
            table = Table(title="Your Clusters")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Provider", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Expires In", style="red")

            for c in clusters:
                table.add_row(c['id'], c['name'], c['provider'], c['status'], c['expires_in'])

            console.print(table)
        except APIError as e:
            console.print(f"[bold red]Error:[/bold red] {e.message}")

12.2 Configuration File Templates
CLI ~/.config/pyk8s-lab/config.yaml:

api_url: "https://api.pyk8s-lab.io"
current_user: "user@example.com"
auth:
  # JWTs are stored here by the 'auth login' command
  access_token: "ey..."
  refresh_token: "ey..."

Helm production-values.yaml:

# Example production values
global:
  imageRegistry: "our-private-registry.io/pyk8s-lab"
  pyk8sLabVersion: "1.2.0" # Pin to a specific version

apiService:
  replicaCount: 3
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 8
  
postgresql:
  enabled: false # Use external managed database

redis:
  enabled: false # Use external managed cache

ingress:
  hostname: "app.pyk8s-lab.io"
  tls:
    enabled: true
    secretName: "pyk8s-lab-tls-cert"

secrets:
  # Using Vault injector, so no direct secrets here
  vaultIntegration:
    enabled: true

12.3 Environment Setup Instructions
Local Development Makefile:

.PHONY: setup install-hooks test clean

setup:
	python -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"

install-hooks:
	pip install pre-commit
	pre-commit install

lint:
	pre-commit run --all-files

test:
	pytest

clean:
	rm -rf .venv .pytest_cache

12.4 Glossary of Terms and Acronyms
• E2E: End-to-End
• gRPC: Google Remote Procedure Call
• HPA: Horizontal Pod Autoscaler
• JWT: JSON Web Token
• KinD: Kubernetes in Docker
• KPI: Key Performance Indicator
• OIDC: OpenID Connect
• RBAC: Role-Based Access Control
• SCA: Software Composition Analysis
• TDD: Technical Design Document
• TTL: Time-To-Live
12.5 References and External Dependencies
• FastAPI: https://fastapi.tiangolo.com/
• SQLAlchemy: https://www.sqlalchemy.org/
• KinD: https://kind.sigs.k8s.io/
• Helm: https://helm.sh/
• Playwright: https://playwright.dev/
• k6: https://k6.io/
12.6 Migration Guides and Upgrade Paths
Upgrading from v1.x to v2.0:
• Breaking Changes:
    ◦ The /api/v1/ endpoint prefix is being deprecated in favor of /api/v2/.
    ◦ The database schema for clusters includes a new mandatory region field.
• Migration Steps:
    1. Pause new cluster creation.
    2. Apply the Alembic database migration script: alembic upgrade head. This will backfill the region column with a default value.
    3. Deploy the new v2.0.0 Helm chart. The new application version will be backwards compatible with CLI clients using v1 for a grace period.
    4. Update CLI clients to the latest version to utilize new features.
    5. After the grace period, support for the v1 API endpoints will be removed.