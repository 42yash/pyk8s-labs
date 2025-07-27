# backend/provisioner.py
import subprocess
from cryptography.fernet import Fernet
from core.config import settings

# Initialize the Fernet cipher with the key from our settings
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    """Encrypts a string and returns it as a string."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts a string and returns it."""
    return fernet.decrypt(encrypted_data.encode()).decode()

def create_kind_cluster(cluster_name: str) -> bool:
    """
    Creates a KinD cluster.
    Returns True on success, False on failure.
    """
    try:
        # The 'check=True' flag will raise a CalledProcessError if the command fails.
        # We also capture output to help with debugging.
        command = ["kind", "create", "cluster", "--name", cluster_name]
        print(f"Running command: {' '.join(command)}")
        subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"Successfully created cluster: {cluster_name}")
        return True
    except subprocess.CalledProcessError as e:
        # Log the error here for debugging. This is critical.
        print(f"Error creating cluster {cluster_name}.")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return False

def get_kind_kubeconfig(cluster_name: str) -> str | None:
    """
    Retrieves the kubeconfig for a given KinD cluster.
    Returns the kubeconfig string or None if an error occurs.
    """
    try:
        command = ["kind", "get", "kubeconfig", "--name", cluster_name]
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting kubeconfig for {cluster_name}: {e.stderr}")
        return None

def delete_kind_cluster(cluster_name: str) -> bool:
    """
    Deletes a KinD cluster.
    Returns True on success, False on failure.
    """
    try:
        command = ["kind", "delete", "cluster", "--name", cluster_name]
        print(f"Running command: {' '.join(command)}")
        subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"Successfully deleted cluster: {cluster_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error deleting cluster {cluster_name}: {e.stderr}")
        return False