# **PyK8s-Lab: On-Demand Kubernetes Playground**

PyK8s-Lab is a self-service, on-demand Kubernetes playground designed to provide developers and learners with ephemeral, isolated Kubernetes clusters. The primary goal of this prototype is to validate the core functionality: provisioning and managing temporary Kubernetes clusters through a simple web interface and a command-line tool.

## **Architecture Overview**

The application consists of three main services managed by Docker Compose:

*   **`frontend`**: A Next.js and React application that serves as the user-facing dashboard for creating and managing clusters.
*   **`backend`**: A Python FastAPI application that provides a REST API for all operations, manages user authentication, and orchestrates cluster provisioning using KinD (Kubernetes in Docker).
*   **`db`**: A PostgreSQL database for storing user and cluster information.

## **Prerequisites**

Before you begin, ensure you have the following installed on your system:
*   Docker
*   Docker Compose

## **Environment Setup**

Setting up the development environment involves one critical step: configuring permissions for the backend service to interact with the Docker daemon on your host machine.

1.  **Clone the repository** (if you haven't already).
2.  **Set the Docker Group ID (GID):** The backend container needs to run with the same Docker group ID as your host system to control the Docker socket (`/var/run/docker.sock`).

    Export the `DOCKER_GID` environment variable by running the following command in your terminal. You must run this in the same shell session where you will run the `docker-compose` commands.
    ```bash
    export DOCKER_GID=$(getent group docker | cut -d: -f3)
    ```
    This command retrieves the numeric GID of the `docker` group on your system and exports it. The `docker-compose.yml` file is configured to pass this variable into the backend container during the build process.

There are no `.env` files to create for development, as all necessary environment variables are defined directly in the `docker-compose.yml` file for simplicity.

## **Running the Development Environment**

Two helper scripts are provided in the root directory to manage the application lifecycle.

### **Standard Restart**

For most development tasks, this is the recommended command to use. It will stop, rebuild any changed services, and restart the application.

```bash
./restart.sh
```
This script intelligently uses Docker's cache and will only rebuild containers if their configuration (e.g., `Dockerfile`, `requirements.txt`, `package.json`) has changed. It also automatically applies any pending database migrations after starting the services.

### **Clean Restart (Nuke and Pave)**

If you encounter issues with dependencies, Docker volumes, or build caches, you can perform a complete reset of the environment.

```bash
./clean-restart.sh
```
This script is more aggressive and will:
1.  Stop and remove all containers, volumes, and networks defined in `docker-compose.yml`.
2.  Prune the Docker system cache to remove any dangling images.
3.  Delete `node_modules` and `.next` from the `frontend` directory.
4.  Rebuild all images from scratch and start the services.
5.  Apply all database migrations.

### **Direct Docker Compose Usage**

You can also use `docker-compose` commands directly:
```bash
# Build and start all services in detached mode
docker-compose up --build -d

# Stop all services
docker-compose down

# Stop services and remove volumes (data will be lost)
docker-compose down -v
```

## **Accessing the Application**

Once the services are running, you can access them at the following URLs:

*   **Frontend (Web UI)**: [http://localhost:3000](http://localhost:3000)
*   **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## **Backend Database Migrations**

The `restart.sh` and `clean-restart.sh` scripts automatically handle applying database migrations using Alembic. However, if you need to create a new migration after changing a SQLAlchemy model, follow these steps:

1.  **Generate a new migration script:**
    After modifying a model in `backend/models/`, run the following command. It executes `alembic revision` as the `root` user inside the container to ensure it can write the new file.
    ```bash
    docker-compose exec --user root backend alembic revision --autogenerate -m "Your descriptive migration message"
    ```

2.  **Fix File Permissions:**
    The previous command creates the new migration file as the `root` user. You must change its ownership back to your current host user to be able to edit or commit it.
    ```bash
    sudo chown -R $USER:$USER backend/alembic/
    ```

3.  **Apply the Migration:**
    Run the standard restart script or apply the migration manually with the following command:
    ```bash
    docker-compose exec backend alembic upgrade head
    ```