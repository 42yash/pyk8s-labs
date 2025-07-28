Development Plan: Removing WebSockets

This document outlines the step-by-step process for completely removing WebSockets from the PyK8s-Lab project and replacing the functionality with more stable, HTTP-based alternatives: Server-Sent Events (SSE) for real-time updates and a "Command Runner" for cluster interaction.
Phase 1: Replace Real-Time Status Updates with Server-Sent Events (SSE)

Goal: To replace the WebSocket-based status update mechanism with a one-way, server-to-client stream using Server-Sent Events (SSE).

    Sub-Phase 1.1: Backend - Implement the SSE Endpoint

        Step 1: In backend/main.py, create a new, authenticated GET endpoint at /api/v1/events.

        Step 2: This endpoint will be an async function that returns a StreamingResponse from FastAPI. The media type should be set to text/event-stream.

        Step 3: The endpoint's logic will subscribe to the existing REDIS_CHANNEL. It will loop indefinitely, listening for messages from Redis.

        Step 4: When a message is received, the endpoint will format it as an SSE message (e.g., data: {"cluster_id": "...", "status": "RUNNING"}\n\n) and yield it to the client.

        Step 5: Ensure the endpoint handles client disconnects gracefully to stop the Redis listening loop and clean up resources.

    Sub-Phase 1.2: Frontend - Consume SSE for Status Updates

        Step 1: In frontend/src/lib/store/apiSlice.js, locate the onCacheEntryAdded function within the getClusters query definition.

        Step 2: Remove the entire WebSocket client implementation.

        Step 3: In its place, instantiate the native browser EventSource object, pointing it to the new /api/v1/events endpoint. The user's authentication token must be included as a query parameter.

        Step 4: Add a listener for the onmessage event of the EventSource object.

        Step 5: The logic inside the onmessage listener will be similar to the old WebSocket logic: parse the event.data JSON and use updateCachedData to update the status of the relevant cluster in the Redux Toolkit cache.

    Sub-Phase 1.3: Backend - Code Cleanup

        Step 1: In backend/main.py, completely remove the @app.websocket("/api/v1/ws") endpoint and its associated logic.

        Step 2: Delete the backend/websocket_manager.py file, as the ConnectionManager class is no longer needed.

        Step 3: Remove the websockets library from backend/requirements.txt.

Phase 2: Replace Interactive Terminal

Goal: To replace the complex, WebSocket-based interactive terminal with a simpler, more reliable "Command Runner" that operates over standard REST API calls.

    Sub-Phase 2.1: Backend - Create Command Execution Endpoint

        Step 1: In backend/api.py, create a new POST endpoint at /clusters/{cluster_id}/exec.

        Step 2: This endpoint will expect a JSON payload containing the command to be executed, for example: {"command": "kubectl get pods"}.

        Step 3: The endpoint logic will validate the cluster ownership and status (RUNNING).

        Step 4: It will use the docker.client to execute the command inside the cluster's control-plane container using container.exec_run(). This call will be non-blocking and will capture the stdout and stderr of the command.

        Step 5: The endpoint will return a JSON response containing the captured output, for example: {"output": "...", "error": "..."}.

    Sub-Phase 2.2: Frontend - Rework the Terminal Component

        Step 1: In frontend/src/components/Terminal.js, remove all dependencies and logic related to xterm.js and WebSockets.

        Step 2: Redesign the component to be a "Command Runner". It should contain:

            An input field for the user to type their command.

            A "Run" button.

            A display area (e.g., a <pre> tag with a dark background) to show the output from the command.

        Step 3: In frontend/src/lib/store/apiSlice.js, create a new RTK Query mutation named executeClusterCommand. This mutation will call the new POST /clusters/{cluster_id}/exec endpoint.

        Step 4: The "Run" button's onClick handler will trigger this mutation with the current command from the input field. The component will then display the data or error from the mutation's result in the output area.

        Step 5: Update the "Terminal" button in frontend/src/app/dashboard/page.js so that it opens this new "Command Runner" modal.

Phase 3: Final Cleanup & Verification

Goal: To remove all remaining traces of the old implementation and ensure the new system is working correctly.

    Step 1: Dependency Removal

        Run npm uninstall xterm in the frontend directory to remove the library.

        Verify websockets has been removed from backend/requirements.txt and rebuild the backend container (./restart.sh).

    Step 2: End-to-End Testing

        Manually perform the critical user journeys:

            Log in and create a new cluster. Verify that the status updates from PROVISIONING to RUNNING in the UI automatically (this now uses SSE).

            Open the "Command Runner" for the running cluster. Execute a simple command like kubectl version and verify the output is displayed correctly.

            Delete the cluster and verify it is removed from the UI automatically.

        Update any automated E2E tests (e.g., Playwright scripts) to reflect the new UI and functionality.

    Step 3: Documentation Update

        Review all documents in the docs/ directory.

        Archive or delete old development plans (dev_plan_1.md, dev_plan_2.md, dev_plan_3.md).

        Update the main technical_document.md to remove references to WebSockets and describe the new SSE and Command Runner architecture.