## **PyK8s-Lab: Final Development Plan (Prototype V0.1)**

This plan guides a developer from the current state of the repository to a feature-complete prototype. It is broken down into logical phases, addressing the major components that are not yet implemented.

### **Phase 0: Project Review and Environment Validation**

**Goal:** To confirm the current codebase is fully functional and establish a stable baseline before adding new features.

1.  **Environment Setup & Verification:**
    *   From the project root, ensure Docker is running and execute the `clean-restart.sh` script. This will build the containers, start the services, and apply database migrations.
    *   Verify that all services start without errors by checking `docker-compose logs -f`.
    *   Confirm you can access the frontend at `http://localhost:3000` and the backend API documentation at `http://localhost:8000/docs`.

2.  **Core Functionality Test:**
    *   Manually perform the primary user journey:
        *   Navigate to the registration page (`/register`) and create a new user.
        *   Be redirected to the login page (`/login`) and sign in.
        *   On the dashboard (`/dashboard`), create a new cluster.
        *   Observe the cluster status change from `PROVISIONING` to `RUNNING`. (Note: This currently relies on polling; a later phase will upgrade this to WebSockets).
        *   Delete the cluster and confirm it is removed from the list.
    *   This validation ensures that the existing backend logic, database, and frontend state management are all working correctly together.

3.  **Gap Analysis Acknowledgement:**
    *   This plan acknowledges that the following key features from the `technical_document.md` are currently missing and will be the focus of the subsequent phases:
        *   **Real-time updates via WebSockets.**
        *   **The Python-based Command-Line Interface (CLI).**
        *   **Helm chart for Kubernetes deployment.**
        *   **A formal testing suite (unit, integration, and E2E).**
        *   **Redis service for Pub/Sub messaging.**

### **Phase 1: Implementing Real-Time Status Updates with WebSockets**

**Goal:** To replace the frontend's polling mechanism with a WebSocket connection for instant, push-based status updates, as specified in the technical document.

1.  **Backend Infrastructure - Adding Redis:**
    *   Modify `docker-compose.yml` to include a new `redis` service (e.g., using the `redis:alpine` image). Make the `backend` service depend on it.
    *   Add `redis` to the `backend/requirements.txt` file to install the Python client library.
    *   Update `backend/core/config.py` to include configuration variables for the Redis host and port.
    *   Rebuild the backend container (`docker-compose build backend`) to include the new dependency.

2.  **Backend Logic - WebSocket and Pub/Sub:**
    *   In a new file, `backend/websockets.py`, create a connection manager class. This class will handle authenticating WebSocket connections (via a token in the query params), and storing active connections (e.g., in a dictionary mapping user IDs to connection objects).
    *   Create a new WebSocket endpoint in `backend/api.py`, such as `/ws`. This endpoint will use the connection manager to handle new client connections.
    *   Modify the `run_cluster_provisioning` and `run_cluster_deletion` background tasks in `backend/api.py`. At critical steps (e.g., after starting creation, after a success, after an error), publish a status update message to a Redis Pub/Sub channel. The message should contain the `cluster_id` and the new `status`.
    *   Implement the listener logic within your `websockets.py` manager. It should subscribe to the Redis Pub/Sub channel and, upon receiving a message, find the corresponding user's WebSocket connection and send the status update to the client.

3.  **Frontend Integration - Consuming WebSocket Events:**
    *   In `frontend/src/app/dashboard/page.js`, remove the `pollingInterval` option from the `useGetClustersQuery` hook.
    *   Create a new custom React hook (e.g., `useClusterWebSocket`) or a Redux Toolkit listener middleware to manage the WebSocket lifecycle.
    *   When a user logs in and the dashboard loads, this new logic should establish a connection to the backend's `/ws` endpoint, passing the auth token.
    *   When a status update message is received from the WebSocket, dispatch an action to update the RTK Query cache for the specific cluster. This will cause the UI to re-render with the new status badge automatically and instantly.

### **Phase 2: Developing the Command-Line Interface (CLI)**

**Goal:** To create the `pyk8s` CLI tool for power users, as detailed in section 3.4 of the technical document.

1.  **Project Scaffolding:**
    *   Create a new top-level directory named `cli/`.
    *   Inside `cli/`, initialize a new Python project. Create a `main.py` entrypoint and a `requirements.txt` file.
    *   Add `click`, `rich`, `httpx`, and `pyyaml` to `cli/requirements.txt`.

2.  **Authentication and Configuration:**
    *   In the CLI's `main.py`, implement the `pyk8s auth login` command using `click`.
    *   This command will prompt the user for their email and password. It will then make a POST request to the backend's `/api/v1/auth/token` endpoint using `httpx`.
    *   Upon a successful response, it will create a directory `~/.config/pyk8s-lab/` and save the received JWT and API URL into a `config.yaml` file.
    *   Create helper functions within the CLI to read this configuration file for all subsequent authenticated commands.

3.  **Cluster Management Commands:**
    *   Implement the `pyk8s cluster list` command. It will read the token from the config, make an authenticated `GET` request to `/api/v1/clusters`, and use the `rich` library to display the results in a formatted table.
    *   Implement `pyk8s cluster create --name <name> --ttl-hours <hours>`. This command will make an authenticated `POST` request to `/api/v1/clusters`.
    *   Implement `pyk8s cluster delete <name>`. This command will first need to list the clusters to find the ID corresponding to the given name, and then make an authenticated `DELETE` request to `/api/v1/clusters/{cluster_id}`.

4.  **Kubeconfig Retrieval:**
    *   **Backend Enhancement:** First, create a new protected endpoint in `backend/api.py`: `GET /clusters/{cluster_id}/kubeconfig`. This endpoint will fetch the cluster, verify it belongs to the `current_user`, decrypt the `encrypted_kubeconfig` field using the `provisioner.py` utility, and return the decrypted kubeconfig as a plain text response.
    *   **CLI Command:** Implement the `pyk8s cluster get-kubeconfig <name>` command. It will find the cluster ID by name, call the new `/kubeconfig` endpoint, and print the response directly to standard output, allowing users to pipe it to a file (e.g., `pyk8s ... > my-cluster.yaml`).

### **Phase 3: Finalizing for Deployment**

**Goal:** To prepare the application for a production-like deployment by creating a Helm chart and optimizing the Docker images.

1.  **Production-Ready Frontend Dockerfile:**
    *   Modify the `frontend/Dockerfile` to use a multi-stage build.
    *   The first stage (`builder`) will use a full `node` image, copy `package.json`, run `npm install`, copy the source code, and run `npm run build`.
    *   The final stage will use a lightweight image (e.g., `node:18-alpine`), copy the built artifacts (the `.next` directory) from the `builder` stage, and set the `CMD` to `npm start` to run the optimized Next.js server.

2.  **Helm Chart Creation:**
    *   Create a new top-level directory named `helm/`.
    *   Inside, create a Helm chart for the `pyk8s-lab` application.
    *   Develop templates for the backend `Deployment`, `Service`, and an `Ingress` resource.
    *   Create a `Secret` template to manage the database credentials, `SECRET_KEY`, and `ENCRYPTION_KEY`.
    *   Externalize all configurable values (image tags, replica counts, service ports, domain names for the ingress) into the `values.yaml` file.
    *   Update the chart dependencies to include PostgreSQL and Redis from a public chart repository (e.g., Bitnami), so the entire stack can be deployed with one command.

3.  **Documentation Cleanup:**
    *   Edit the root `README.md` file. Remove the development scratchpad notes.
    *   Add a clear, comprehensive "Getting Started" section that explains how to set environment variables (like `DOCKER_GID`) and run the project using `docker-compose` or the provided scripts.
    *   Add a brief architecture overview.

### **Phase 4: Implementing a Testing Strategy**

**Goal:** To ensure the prototype is robust and reliable by adding unit, integration, and end-to-end tests.

1.  **Backend Testing (`pytest`):**
    *   In the `backend/` directory, create a `tests/` folder.
    *   Write unit tests for non-API logic. For example, test `provisioner.py` functions by mocking Python's `subprocess.run`.
    *   Write integration tests for the API endpoints using FastAPI's `TestClient`. Configure these tests to use a separate, temporary test database to avoid interfering with development data. Test user creation, login, and the full cluster CRUD lifecycle.

2.  **Frontend Testing (`Jest` & `React Testing Library`):**
    *   In the `frontend/` directory, set up Jest and React Testing Library.
    *   Write unit tests for key UI components. For example, test the `DashboardLayout` to ensure it renders user information correctly. Test the cluster creation form to check input validation and button states.

3.  **End-to-End Testing (`Playwright`):**
    *   Create a new top-level `e2e/` directory.
    *   Set up Playwright for automated browser testing.
    *   Write a single, critical test script that covers the main user journey:
        1.  Navigate to the site and register a new user.
        2.  Log in with the new credentials.
        3.  Create a new cluster.
        4.  Wait for the WebSocket event to update the cluster's status to `RUNNING`.
        5.  Delete the cluster.
        6.  Log out.
    *   This E2E test will validate that all parts of the system—frontend, backend, database, and WebSockets—are working together correctly.