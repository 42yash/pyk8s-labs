# cli/main.py
import getpass
import sys
from pathlib import Path

import click
import httpx
import yaml
from rich.console import Console
from rich.table import Table

# --- Configuration ---
API_BASE_URL = "http://localhost:8000/api/v1"
CONFIG_DIR = Path.home() / ".config" / "pyk8s-lab"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
CONSOLE = Console()
# --- START: NEW TIMEOUT CONFIGURATION ---
TIMEOUT = 30.0  # A more generous 30-second timeout for all API calls
# --- END: NEW TIMEOUT CONFIGURATION ---


# --- Helper Functions ---
def save_config(data: dict):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(data, f)
        CONFIG_FILE.chmod(0o600)
    except Exception as e:
        CONSOLE.print(f"[bold red]Error saving configuration:[/bold red] {e}")
        sys.exit(1)

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        CONSOLE.print(f"[bold red]Error:[/bold red] Not logged in. Please run '[cyan]pyk8s auth login[/cyan]' first.")
        sys.exit(1)
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        CONSOLE.print(f"[bold red]Error loading configuration:[/bold red] {e}")
        sys.exit(1)

def get_auth_headers() -> dict:
    config = load_config()
    token = config.get("access_token")
    if not token:
        CONSOLE.print(f"[bold red]Error:[/bold red] Access token not found. Please run '[cyan]pyk8s auth login[/cyan]' again.")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}

# --- Click Command Structure ---
@click.group()
def cli():
    """PyK8s-Lab CLI for managing ephemeral Kubernetes clusters."""
    pass

# --- Auth Group ---
@cli.group()
def auth():
    """Manage authentication."""
    pass

@auth.command()
def login():
    """Log in to the PyK8s-Lab API and save the token."""
    CONSOLE.print("[bold cyan]PyK8s-Lab Login[/bold cyan]")
    email = click.prompt("Email")
    password = getpass.getpass("Password: ")
    try:
        with CONSOLE.status("[bold green]Authenticating...[/bold green]", spinner="dots"):
            form_data = {"username": email, "password": password}
            # Add timeout to the client
            with httpx.Client(timeout=TIMEOUT) as client:
                response = client.post(f"{API_BASE_URL}/auth/token", data=form_data)
                response.raise_for_status()
        token_data = response.json()
        config_to_save = {"api_url": API_BASE_URL, "access_token": token_data["access_token"]}
        save_config(config_to_save)
        CONSOLE.print(f"✅ [bold green]Login successful![/bold green] Configuration saved to [cyan]{CONFIG_FILE}[/cyan].")
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]Error:[/bold red] API returned status {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection or Timeout Error:[/bold red] Could not communicate with the API at [cyan]{API_BASE_URL}[/cyan]. ({e})")

# --- Cluster Group ---
@cli.group()
def cluster():
    """Manage clusters."""
    pass

@cluster.command("list")
def list_clusters():
    """List all your clusters."""
    try:
        headers = get_auth_headers()
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(f"{API_BASE_URL}/clusters", headers=headers)
            response.raise_for_status()
        clusters_data = response.json()
        table = Table(title="Your Clusters")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", justify="right", style="magenta")
        table.add_column("Expires At", justify="right", style="green")
        table.add_column("ID", style="dim")
        for c in clusters_data:
            table.add_row(c['name'], c['status'], c['ttl_expires_at'], c['id'])
        CONSOLE.print(table)
    except Exception as e:
        CONSOLE.print(f"[bold red]An error occurred:[/bold red] {e}")

@cluster.command("create")
@click.option("--name", required=True, help="The name for the new cluster.")
@click.option("--ttl-hours", default=1, type=int, help="Time-to-live for the cluster in hours.")
def create_cluster(name: str, ttl_hours: int):
    """Create a new cluster."""
    try:
        headers = get_auth_headers()
        payload = {"name": name, "ttl_hours": ttl_hours}
        with CONSOLE.status(f"[bold green]Sending request to create cluster '{name}'...[/bold green]"):
            with httpx.Client(timeout=TIMEOUT) as client:
                response = client.post(f"{API_BASE_URL}/clusters", headers=headers, json=payload)
                response.raise_for_status()
        CONSOLE.print(f"✅ [bold green]Request accepted![/bold green] Cluster '{name}' is now provisioning.")
        CONSOLE.print("   Run '[cyan]pyk8s cluster list[/cyan]' to check its status.")
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]Error:[/bold red] API returned status {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection or Timeout Error:[/bold red] Could not communicate with the API. ({e})")

@cluster.command("delete")
@click.argument("name")
def delete_cluster(name: str):
    """Delete a cluster by its name."""
    try:
        headers = get_auth_headers()
        with httpx.Client(timeout=TIMEOUT) as client:
            with CONSOLE.status(f"[bold yellow]Finding cluster '{name}'...[/bold yellow]"):
                get_response = client.get(f"{API_BASE_URL}/clusters", headers=headers)
                get_response.raise_for_status()
            clusters_data = get_response.json()
            cluster_to_delete = next((c for c in clusters_data if c['name'] == name), None)
            if not cluster_to_delete:
                CONSOLE.print(f"[bold red]Error:[/bold red] Cluster '{name}' not found.")
                return
            cluster_id = cluster_to_delete['id']
            with CONSOLE.status(f"[bold red]Sending request to delete cluster '{name}'...[/bold red]"):
                delete_response = client.delete(f"{API_BASE_URL}/clusters/{cluster_id}", headers=headers)
                delete_response.raise_for_status()
        CONSOLE.print(f"✅ [bold green]Request accepted![/bold green] Cluster '{name}' is scheduled for deletion.")
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]Error:[/bold red] API returned status {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection or Timeout Error:[/bold red] Could not communicate with the API. ({e})")

@cluster.command("get-kubeconfig")
@click.argument("name")
def get_kubeconfig(name: str):
    """
    Get the kubeconfig for a cluster and print it to stdout.
    
    Example: pyk8s cluster get-kubeconfig my-cluster > my-cluster.yaml
    """
    try:
        headers = get_auth_headers()
        with httpx.Client(timeout=TIMEOUT) as client:
            with CONSOLE.status(f"[bold yellow]Finding cluster '{name}'...[/bold yellow]"):
                get_response = client.get(f"{API_BASE_URL}/clusters", headers=headers)
                get_response.raise_for_status()

            clusters_data = get_response.json()
            cluster_to_get = next((c for c in clusters_data if c['name'] == name), None)

            if not cluster_to_get:
                CONSOLE.print(f"[bold red]Error:[/bold red] Cluster '{name}' not found.")
                sys.exit(1)
            
            if cluster_to_get['status'] != 'RUNNING':
                CONSOLE.print(f"[bold red]Error:[/bold red] Kubeconfig is only available for clusters in 'RUNNING' status. Status is currently '{cluster_to_get['status']}'.")
                sys.exit(1)

            cluster_id = cluster_to_get['id']

            with CONSOLE.status(f"[bold green]Fetching kubeconfig for '{name}'...[/bold green]"):
                kubeconfig_response = client.get(f"{API_BASE_URL}/clusters/{cluster_id}/kubeconfig", headers=headers)
                kubeconfig_response.raise_for_status()
            
            print(kubeconfig_response.text)
            
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]Error:[/bold red] API returned status {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
        sys.exit(1)
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection or Timeout Error:[/bold red] Could not communicate with the API. ({e})")
        sys.exit(1)

if __name__ == "__main__":
    cli.add_command(auth)
    cli.add_command(cluster)
    cli()