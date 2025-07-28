# backend/provisioner.py
import subprocess
from cryptography.fernet import Fernet
from core.config import settings

fernet = Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    return fernet.decrypt(encrypted_data.encode()).decode()


def create_cluster(cluster_name: str, provider: str) -> bool:
    if provider == "kind":
        command = ["kind", "create", "cluster", "--name", cluster_name]
    else:
        print(f"Unsupported provider: {provider}")
        return False
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating cluster {cluster_name}: {e.stderr}")
        return False


def get_kubeconfig(cluster_name: str, provider: str) -> str | None:
    if provider == "kind":
        command = ["kind", "get", "kubeconfig", "--name", cluster_name]
    else:
        print(f"Unsupported provider: {provider}")
        return None
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting kubeconfig for {cluster_name}: {e.stderr}")
        return None


def delete_cluster(cluster_name: str, provider: str) -> bool:
    if provider == "kind":
        command = ["kind", "delete", "cluster", "--name", cluster_name]
    else:
        print(f"Unsupported provider: {provider}")
        return False
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error deleting cluster {cluster_name}: {e.stderr}")
        return False
