### **PyK8s-Lab: V1.0 Development Plan**

This plan outlines the major phases of work required to enhance the existing prototype with advanced features, preparing it for a full V1.0 release.

---

### **Phase 1: Backend Foundation for V1.0 Features**

**Goal:** To expand the backend's data models and API to support team management and multi-provider clusters before any UI is built.

*   **Sub-Phase 1.1: Database Schema Expansion**
    *   **Step 1:** Modify the SQLAlchemy models in `backend/models/`. Create a new `team.py` file for the `Team` and `TeamMembership` models. Update the `User` and `Cluster` models to include the new relationships.
    *   **Step 2:** Add a `provider` field to the `Cluster` model to store the Kubernetes distribution type (e.g., 'kind', 'k3s').
    *   **Step 3:** After saving the model changes, generate a new database migration file by running the `alembic revision --autogenerate` command inside the backend container.
    *   **Step 4:** Review the generated migration script for correctness, then apply it to the development database by restarting the services with the `./restart.sh` script.

*   **Sub-Phase 1.2: Implement Team Management Logic**
    *   **Step 1:** Create new Pydantic schemas in `backend/schemas/` for team-related data (e.g., `TeamCreate`, `TeamMember`).
    *   **Step 2:** Implement new CRUD functions in `backend/crud.py` for all team and membership operations (e.g., `create_team`, `add_user_to_team`).
    *   **Step 3:** Implement the new API endpoints in `backend/api.py`. This includes creating a new API router for `/teams` and adding endpoints for creating teams, inviting members, and listing teams.

*   **Sub-Phase 1.3: Implement Role-Based Authorization (RBAC)**
    *   **Step 1:** In `backend/core/security.py`, create new FastAPI dependency functions that can check a user's role within a specific team.
    *   **Step 2:** Apply these new authorization dependencies to the team management endpoints. For example, protect the endpoint for inviting members so that only users with an 'admin' role in that team can use it.

*   **Sub-Phase 1.4: Implement Multi-Provider Provisioning Logic**
    *   **Step 1:** Refactor the `backend/provisioner.py` module. Modify the `create_kind_cluster` function to become a more generic `create_cluster` function that accepts a provider type.
    *   **Step 2:** Implement the logic within this function to select and execute the correct command-line tool based on the chosen provider (e.g., `kind create` vs. `k3d cluster create`).
    *   **Step 3:** Update the `POST /clusters` API endpoint to accept the new `provider` field in its request body and pass it to the provisioning background task.

---

### **Phase 2: Frontend Implementation for Team Management**

**Goal:** To build the user interface that allows users to interact with the new team management features.

*   **Sub-Phase 2.1: API Layer Integration**
    *   **Step 1:** In `frontend/src/lib/store/apiSlice.js`, add new RTK Query endpoint definitions for all the new team-related API endpoints (`getTeams`, `createTeam`, `inviteMember`, etc.).

*   **Sub-Phase 2.2: Build UI Components and Pages**
    *   **Step 1:** Create a new page route in `frontend/src/app/dashboard/teams/` for the main team management view.
    *   **Step 2:** Develop reusable React components for displaying a list of teams, a list of members within a team, and a form for inviting new members.
    *   **Step 3:** Integrate these components into the new teams page, using the RTK Query hooks to fetch and display data.
    *   **Step 4:** Modify the cluster creation modal to include an option to assign the new cluster to a team the user belongs to.

*   **Sub-Phase 2.3: Implement Frontend Authorization**
    *   **Step 1:** Use the user's role information (fetched from the backend) to conditionally render UI elements. For example, the "Invite Member" button should only be visible to users with an 'admin' role in the selected team.

---

### **Phase 3: CLI Enhancement**

**Goal:** To update the CLI to support all new V1.0 backend features, ensuring parity with the web dashboard.

*   **Sub-Phase 3.1: Add Team Management Commands**
    *   **Step 1:** In `cli/main.py`, create a new `click` command group named `team`.
    *   **Step 2:** Implement the subcommands under this group: `create`, `list`, `invite`, and `members`. These commands will make authenticated calls to the new backend API endpoints.
    *   **Step 3:** Use the `rich` library to ensure the output of these commands is well-formatted and user-friendly.

*   **Sub-Phase 3.2: Update Cluster Commands**
    *   **Step 1:** Modify the `pyk8s cluster create` command to accept new options: `--team <team-name>` and `--provider <provider-type>`.
    *   **Step 2:** Update the command's logic to pass these new values in the payload when calling the backend API.

---

### **Phase 4: Advanced Feature Integration (Web Terminal)**

**Goal:** To implement the interactive web terminal for direct cluster access from the UI.

*   **Sub-Phase 4.1: Backend WebSocket for TTY Streaming**
    *   **Step 1:** Create a new, separate WebSocket endpoint in `backend/api.py`, for example at `/ws/terminal/{cluster_id}`.
    *   **Step 2:** Implement the backend logic for this endpoint. When a client connects, the backend will need to use `subprocess` or a similar library to `exec` into the running KinD container.
    *   **Step 3:** Implement two-way streaming to pipe the standard input, output, and error streams between the container's shell and the user's WebSocket connection.

*   **Sub-Phase 4.2: Frontend Terminal Integration**
    *   **Step 1:** Add the `xterm.js` library as a new frontend dependency.
    *   **Step 2:** Create a new `Terminal` React component that initializes an `xterm.js` instance.
    *   **Step 3:** In this component, implement the client-side WebSocket logic to connect to the new terminal endpoint and handle the two-way data streaming between the user's browser and the backend.
    *   **Step 4:** Add a "Terminal" button or tab to the cluster details view in the dashboard to launch this component.

---

### **Phase 5: Production Hardening and Deployment**

**Goal:** To prepare the application for a stable, scalable, and observable production deployment.

*   **Sub-Phase 5.1: Create Production Helm Chart**
    *   **Step 1:** Create a new top-level directory named `helm/`.
    *   **Step 2:** Inside this directory, generate the standard Helm chart structure.
    *   **Step 3:** Develop templates for all necessary Kubernetes resources: `Deployment`, `Service`, `Secret`, `ConfigMap`, and `Ingress` for each of the application's components.
    *   **Step 4:** Externalize all configurable parameters (image tags, replica counts, resource limits, domain names) into the `values.yaml` file.

*   **Sub-Phase 5.2: Implement Operational Readiness Features**
    *   **Step 1:** Add two new endpoints to the FastAPI application in `backend/main.py`: `/health/live` and `/health/ready`.
    *   **Step 2:** Configure the `Deployment` template in the Helm chart to use these endpoints for Kubernetes liveness and readiness probes.
    *   **Step 3:** Update the root `README.md` to remove development-specific notes and add a clear "Getting Started" section and architecture overview. Add instructions for deploying the application using the new Helm chart.

---

### **Phase 6: Comprehensive Testing**

**Goal:** To implement the full testing strategy defined in the technical document to ensure V1.0 is robust and reliable.

*   **Sub-Phase 6.1: Expand Test Suites**
    *   **Step 1:** Write `pytest` integration tests for all new backend API endpoints related to teams and multi-provider cluster creation.
    *   **Step 2:** Write `Jest` and `React Testing Library` tests for all new frontend components related to team management.

*   **Sub-Phase 6.2: Implement End-to-End Testing**
    *   **Step 1:** Set up the `Playwright` testing framework in a new top-level `e2e/` directory.
    *   **Step 2:** Write the critical E2E test script that covers the new team-based workflow: user A creates a team, invites user B, user B logs in and creates a cluster for that team, and user A can see and delete the cluster.
    *   **Step 3:** Configure the CI/CD pipeline to run these E2E tests against a staging environment.