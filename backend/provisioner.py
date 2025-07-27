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

def create_cluster(cluster_name: str, provider: str) -> bool:
    """
    Creates a Kubernetes cluster using the specified provider.
    Returns True on success, False on failure.
    """
    command = []
    if provider == 'kind':
        command = ["kind", "create", "cluster", "--name", cluster_name]
    elif provider == 'k3d':
        # Placeholder for k3d logic
        # command = ["k3d", "cluster", "create", cluster_name]
        print(f"Provider 'k3d' is not yet implemented.")
        return False
    else:
        print(f"Unsupported provider: {provider}")
        return False

    try:
        print(f"Running command: {' '.join(command)}")
        subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"Successfully created cluster: {cluster_name} with provider {provider}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating cluster {cluster_name} with provider {provider}.")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return False

def get_kubeconfig(cluster_name: str, provider: str) -> str | None:
    """
    Retrieves the kubeconfig for a given cluster.
    Returns the kubeconfig string or None if an error occurs.
    """
    command = []
    if provider == 'kind':
        command = ["kind", "get", "kubeconfig", "--name", cluster_name]
    elif provider == 'k3d':
        # command = ["k3d", "kubeconfig", "get", cluster_name]
        print(f"Provider 'k3d' is not yet implemented.")
        return None
    else:
        print(f"Unsupported provider: {provider}")
        return None
    
    try:
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

def delete_cluster(cluster_name: str, provider: str) -> bool:
    """
    Deletes a Kubernetes cluster using the specified provider.
    Returns True on success, False on failure.
    """
    command = []
    if provider == 'kind':
        command = ["kind", "delete", "cluster", "--name", cluster_name]
    elif provider == 'k3d':
        # command = ["k3d", "cluster", "delete", cluster_name]
        print(f"Provider 'k3d' is not yet implemented.")
        return False
    else:
        print(f"Unsupported provider: {provider}")
        return False
        
    try:
        print(f"Running command: {' '.join(command)}")
        subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"Successfully deleted cluster: {cluster_name} with provider {provider}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error deleting cluster {cluster_name}: {e.stderr}")
        return False