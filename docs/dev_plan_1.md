Of course. Based on the provided repository snapshot and the V0.1 technical design document, here is a detailed, step-by-step development plan to guide a developer in completing the PyK8s-Lab prototype.

This plan assumes the developer is starting with the code provided in `repomix-output.txt` and aims to achieve the functionality described in the `technical_document.md` for the prototype (V0.1).

***

## **PyK8s-Lab: Detailed Development Plan (Prototype V0.1)**

This guide is broken down into logical phases. Each phase builds upon the last, taking the project from its initial state to a feature-complete prototype.

### **Phase 0: Foundation and Environment Setup**

The goal of this phase is to ensure the development environment is stable, dependencies are correctly configured, and the database is ready for schema changes.

1.  **Verify Docker Compose:**
    *   Run `docker-compose up --build` from the root directory.
    *   Confirm that the `frontend`, `backend`, and `db` services start without errors.
    *   You should be able to access the default Next.js page at `http://localhost:3000` and the backend's "Hello" message at `http://localhost:8000/api/v1`.

2.  **Establish Backend Configuration:**
    *   Inside `backend/app/`, create a `core` directory.
    *   Inside `backend/app/core/`, create a `config.py` file.
    *   Use Pydantic's `BaseSettings` to define and load configuration from environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`). This makes configuration management robust.

3.  **Implement Database Migrations:**
    *   Add `alembic` to your `backend/requirements.txt`.
    *   In the `backend/` directory, initialize Alembic by running `alembic init alembic`.
    *   Modify the generated `alembic/env.py` to get the database URL from your new configuration system and to recognize your future SQLAlchemy models.
    *   Modify `alembic.ini` to point to the correct database URL.

### **Phase 1: Backend - User Authentication**

This phase implements the core of user management: registration, login, and token-based authentication.

1.  **Create the User Model and Schema:**
    *   In a new directory `backend/app/models/`, create `user.py`. Define a `User` table using SQLAlchemy, including columns for `id`, `email`, and `hashed_password`.
    *   In a new directory `backend/app/schemas/`, create `user.py`. Define Pydantic schemas for user creation (`UserCreate`), user representation (`User`), and token data (`Token`, `TokenData`).

2.  **Implement Password Hashing and JWT Logic:**
    *   Add `passlib[bcrypt]` and `python-jose[cryptography]` to `backend/requirements.txt`.
    *   Create a `backend/app/core/security.py` file.
    *   In this file, implement functions to:
        *   Hash passwords using `passlib`.
        *   Verify passwords.
        *   Create JWT access tokens.
        *   Decode and verify JWT access tokens.

3.  **Build the User Database Table:**
    *   After defining the `User` model, run `alembic revision --autogenerate -m "Create users table"`.
    *   Inspect the generated migration script in `backend/alembic/versions/` for correctness.
    *   Apply the migration: `alembic upgrade head`. Your `pyk8s_db` will now have the `users` table.

4.  **Create Authentication API Endpoints:**
    *   In `backend/app/main.py`, create a new API router for authentication.
    *   Implement the `POST /users/register` endpoint to create a new user.
    *   Implement the `POST /auth/token` endpoint following the OAuth2 Password Flow to log a user in and return a JWT.

5.  **Secure Endpoints:**
    *   In `security.py`, create a FastAPI dependency that gets the current user from the `Authorization` header's JWT.
    *   You can now protect other future endpoints by adding this dependency.

### **Phase 2: Backend - Cluster Management**

This phase delivers the project's core value: provisioning and managing KinD clusters.

1.  **Create the Cluster Model and Schema:**
    *   In `backend/app/models/`, create `cluster.py`. Define a `Cluster` table with columns for `id`, `name`, `status`, `user_id` (foreign key), `encrypted_kubeconfig`, and `ttl_expires_at`.
    *   In `backend/app/schemas/`, create `cluster.py` with Pydantic schemas for cluster creation and representation.
    *   Generate and apply the database migration using Alembic as you did for the `users` table.

2.  **Implement Cluster Provisioning Logic:**
    *   Create a new file `backend/app/provisioner.py`.
    *   Write a function `create_kind_cluster(cluster_name: str)`. This function will use Python's `subprocess` module to execute `kind create cluster --name <cluster_name>`.
    *   Add a function `get_kind_kubeconfig(cluster_name: str)` that runs `kind get kubeconfig --name <cluster_name>` and returns the output.
    *   Add a function `delete_kind_cluster(cluster_name: str)` that runs `kind delete cluster --name <cluster_name>`.
    *   **Important:** This logic will run inside the backend container. You must mount the host's Docker socket (`/var/run/docker.sock`) into the backend container in `docker-compose.yml` so that it can control Docker to create KinD clusters.

3.  **Build the Cluster API Endpoints:**
    *   Create a new router in `backend/app/main.py` for clusters.
    *   `POST /clusters/`: This endpoint should:
        *   Take a cluster name and TTL duration.
        *   Create a `Cluster` record in the database with `PROVISIONING` status.
        *   Use FastAPI's `BackgroundTasks` to call a worker function. The worker will run the `create_kind_cluster` logic, update the status to `RUNNING` or `ERROR`, retrieve and encrypt the kubeconfig, and save it to the database.
    *   `GET /clusters/`: List all clusters belonging to the authenticated user.
    *   `GET /clusters/{cluster_id}`: Get details for a single cluster.
    *   `DELETE /clusters/{cluster_id}`: Use `BackgroundTasks` to run the `delete_kind_cluster` logic and remove the database record.

4.  **Implement TTL Mechanism:**
    *   Add `apscheduler` to `requirements.txt`.
    *   In `main.py`, set up a `BackgroundScheduler` that runs a job every 5-10 minutes.
    *   The job will query the database for clusters where `ttl_expires_at` is in the past and the status is `RUNNING`. For each expired cluster, it will trigger the deletion background task.

### **Phase 3: Frontend - User Interface**

This phase builds the user-facing web dashboard for interacting with the backend.

1.  **Set Up State Management:**
    *   In the `frontend/` directory, install Redux Toolkit and RTK Query: `npm install @reduxjs/toolkit react-redux`.
    *   Create a directory `frontend/src/app/store/`.
    *   Inside, set up your Redux store and create an RTK Query API slice. Define endpoints that match the backend API (`login`, `register`, `getClusters`, `createCluster`, etc.).

2.  **Implement Authentication Flow:**
    *   Create pages for Login and Registration under `frontend/src/app/(auth)/login` and `frontend/src/app/(auth)/register`.
    *   Build simple forms that use the RTK Query hooks to call the backend.
    *   Upon successful login, store the JWT in a secure client-side location (e.g., an HttpOnly cookie).
    *   Implement a mechanism (e.g., a Higher-Order Component or a layout check) to protect dashboard routes from unauthenticated users.

3.  **Build the Cluster Dashboard:**
    *   Modify the main page at `frontend/src/app/page.js` to be the main dashboard.
    *   Use the `useGetClustersQuery` hook from your API slice to fetch and display a list of the user's clusters.
    *   Create a reusable `ClusterCard.js` component in `frontend/src/components/` to display information for each cluster (name, status, etc.).
    *   Add a "Create Cluster" button that opens a modal or form to start the provisioning process.
    *   Add a "Delete" button to each `ClusterCard`.

### **Phase 4: Real-Time Integration with WebSockets**

Connect the frontend and backend for live status updates during cluster provisioning.

1.  **Backend WebSocket Endpoint:**
    *   Add `websockets` to `requirements.txt`.
    *   In `backend/app/main.py`, create a `GET /ws` endpoint.
    *   The endpoint should expect a JWT as a query parameter for authentication.
    *   Upon successful connection, add the user's connection to a manager/dictionary.
    *   Modify the cluster provisioning worker: after each major step (e.g., "pulling image," "starting control-plane"), it should publish a status update message to a Redis Pub/Sub channel.
    *   The WebSocket endpoint manager will listen to this Redis channel and broadcast messages to the correct connected user.

2.  **Frontend WebSocket Client:**
    *   In the `frontend/` application, create a custom hook or a React Context to manage the WebSocket connection.
    *   Connect to the `/ws` endpoint after the user logs in, passing the JWT.
    *   When a `cluster.status.changed` message is received, dispatch an action to update the cluster's status in the Redux Toolkit store. The UI will automatically re-render with the new status (e.g., changing from "Provisioning" to "Running").

### **Phase 5: CLI Development**

Create the command-line interface for power users.

1.  **Set Up the CLI Project:**
    *   Create a new `cli/` directory in the project root.
    *   Initialize a new Python project with its own `requirements.txt` (including `click`, `rich`, `httpx`, `pyyaml`).
    *   Create a main script, e.g., `cli/main.py`.

2.  **Implement Commands:**
    *   Use `click` to structure the CLI commands as specified in the design document (`pyk8s auth login`, `pyk8s cluster create`, etc.).
    *   `auth login`: Will prompt for email/password and call the `/auth/token` endpoint.
    *   `cluster` commands will read the token from the config file and make authenticated requests to the backend API.

3.  **Manage Configuration and Output:**
    *   Implement logic to securely store the retrieved JWT in `~/.config/pyk8s-lab/config.yaml`.
    *   Use the `rich` library to provide well-formatted output, such as tables for `cluster list`.

### **Phase 6: Deployment and Finalization**

Prepare the application for a production-like deployment.

1.  **Refine Dockerfiles:**
    *   **Backend:** Ensure the `backend/Dockerfile` correctly copies all new modules and installs all new dependencies.
    *   **Frontend:** Modify `frontend/Dockerfile` to perform a multi-stage build. The final stage should copy the output of `npm run build` from a builder stage and use `npm start` to run the optimized Next.js server.

2.  **Create Helm Chart:**
    *   Create a `helm/` directory.
    *   Develop a Helm chart for the `pyk8s-lab` backend.
    *   Include templates for `Deployment`, `Service`, `Ingress`, and `Secret`.
    *   Parameterize key values (image tag, replica count, etc.) in `values.yaml`.

3.  **Documentation:**
    *   Update the root `README.md` to provide a comprehensive overview of the project, architecture, and detailed instructions on how to set up the development environment and run the application.

### **Phase 7: Testing**

Ensure the prototype is robust and reliable.

1.  **Backend Tests (`pytest`):**
    *   Write unit tests for critical business logic (e.g., password hashing, TTL calculation).
    *   Write integration tests for the API endpoints using FastAPI's `TestClient` and a separate test database.

2.  **Frontend Tests (`Jest` & `React Testing Library`):**
    *   Write unit tests for key UI components to ensure they render correctly based on props.

3.  **End-to-End Test (`Playwright`):**
    *   Write a single, critical E2E test script that covers the main user journey: register -> login -> create cluster -> verify cluster is running -> delete cluster. This validates that all parts of the system are working together correctly.