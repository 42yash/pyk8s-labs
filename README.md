# **PyK8s-Lab: On-Demand Kubernetes Playground**

PyK8s-Lab is a self-service, on-demand Kubernetes playground designed to provide developers and learners with ephemeral, isolated Kubernetes clusters. The primary goal of this prototype is to validate the core functionality: provisioning and managing temporary Kubernetes clusters through a simple web interface and a command-line tool.

## **Architecture Overview**

The application consists of four main services managed by Docker Compose:

*   **`frontend`**: A Next.js and React application that serves the user-facing dashboard for creating and managing clusters.
*   **`backend`**: A Python FastAPI application that provides a REST API for all operations, manages user authentication, and orchestrates cluster provisioning using KinD (Kubernetes in Docker).
*   **`db`**: A PostgreSQL database for storing user and cluster information.
*   **`redis`**: A Redis server used for the WebSocket Pub/Sub messaging system to provide real-time status updates.

## **Prerequisites**

Before you begin, ensure you have the following installed on your system:
*   Docker
*   Docker Compose

## **Environment Setup**

Setting up the development environment involves one critical step: creating a `.env` file to configure user permissions for the backend service. This allows the container to interact with the Docker daemon on your host machine without permission errors.

A helper script is provided to automate this. In your terminal, from the root of the project, run:

```bash
./scripts/set_env.sh
```

This script will:
1.  Detect the numeric Group ID (GID) of the `docker` group on your host system.
2.  Detect your current user's numeric User ID (UID).
3.  Create a `.env` file in the project root with these values.

The `docker-compose.yml` file is configured to read this `.env` file and pass the variables into the backend container during the build process, ensuring seamless communication with the Docker socket.

## **Running the Development Environment**

Two helper scripts are provided in the root directory to manage the application lifecycle.

### **Standard Restart**

For most development tasks, this is the recommended command to use. It will stop, rebuild any changed services, and restart the application.

```bash
./restart.sh
```
This script intelligently uses Docker's cache and will only rebuild containers if their configuration (e.g., `Dockerfile`, `requirements.txt`) has changed. It also automatically applies any pending database migrations after starting the services.

### **Clean Restart (Nuke and Pave)**

If you en### Next Steps

1.  **Replace the content** of your root `README.md` file with the markdown text above.

This action concludes **Phase 3**. Our application is now packaged for production deployment, and our documentation is clean and clear for new developers.

We are now ready to begin the final phase of the development plan. Let me know when you are ready to start **Phase 4: Implementing a Testing Strategy**.counter issues with dependencies, Docker volumes, or build caches, you can perform a complete reset of the environment.

```bash
./clean-restart.sh
```
This script is more aggressive and will:
1.  Stop and remove all containers, volumes, and networks.
2.  Prune the Docker system cache to remove any dangling images.
3.  Delete `node_modules` and `.next` from the `frontend` directory.
4.  Rebuild all images from scratch and start the services.
5.  Apply all database migrations.

## **Accessing the Application**

Once the services are running, you can access them at the following URLs:

*   **Frontend (Web UI)**: [http://localhost:3000](http://localhost:3000)
*   **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## **Backend Database Migrations**
### Next Steps

1.  **Replace the content** of your root `README.md` file with the markdown text above.

This action concludes **Phase 3**. Our application is now packaged for production deployment, and our documentation is clean and clear for new developers.

We are now ready to begin the final phase of the development plan. Let me know when you are ready to start **Phase 4: Implementing a Testing Strategy**.
The `restart.sh` and `clean-restart.sh` scripts automatically handle applying database migrations. However, if you need to create a new migration after changing a SQLAlchemy model in `backend/models/`, you must generate the migration file manually.

1.  **Generate the Migration Script:**
    Run the following command. This executes `alembic revision` inside the backend container.
    ```bash
    docker-compose exec backend alembic revision --autogenerate -m "Your descriptive migration message"
    ```

2.  **Apply the New Migration:**
    Simply run the standard restart script, which will apply the newly created migration file.
    ```bash
    ./restart.sh
    ```
