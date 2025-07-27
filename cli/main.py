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
TIMEOUT = 30.0

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

def _get_team_id_from_name(client: httpx.Client, team_name: str) -> str:
    """Helper to resolve a team name to its ID."""
    try:
        headers = get_auth_headers()
        response = client.get(f"{API_BASE_URL}/teams", headers=headers)
        response.raise_for_status()
        teams = response.json()
        
        team = next((t for t in teams if t['name'] == team_name), None)
        
        if not team:
            CONSOLE.print(f"[bold red]Error:[/bold red] Team '{team_name}' not found.")
            sys.exit(1)
        return team['id']
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]API Error:[/bold red] Could not fetch teams. Status {e.response.status_code}.")
        sys.exit(1)
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection Error:[/bold red] {e}")
        sys.exit(1)


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
        table.add_column("Provider", style="green")
        table.add_column("Expires At", justify="right", style="green")
        table.add_column("ID", style="dim")
        for c in clusters_data:
            table.add_row(c['name'], c['status'], c['provider'], c['ttl_expires_at'], c['id'])
        CONSOLE.print(table)
    except Exception as e:
        CONSOLE.print(f"[bold red]An error occurred:[/bold red] {e}")

@cluster.command("create")
@click.option("--name", required=True, help="The name for the new cluster.")
@click.option("--ttl-hours", default=1, type=int, help="Time-to-live for the cluster in hours.")
@click.option("--team", "team_name", help="The name of the team to assign the cluster to.")
@click.option("--provider", type=click.Choice(['kind', 'k3d']), default='kind', help="The Kubernetes provider to use.")
def create_cluster(name: str, ttl_hours: int, team_name: str, provider: str):
    """Create a new cluster."""
    try:
        headers = get_auth_headers()
        payload = {
            "name": name, 
            "ttl_hours": ttl_hours,
            "provider": provider,
        }
        
        with httpx.Client(timeout=TIMEOUT) as client:
            # If a team name is provided, resolve it to an ID and add to payload
            if team_name:
                with CONSOLE.status(f"[bold yellow]Finding team '{team_name}'...[/bold yellow]"):
                    team_id = _get_team_id_from_name(client, team_name)
                payload['team_id'] = team_id

            with CONSOLE.status(f"[bold green]Sending request to create cluster '{name}'...[/bold green]"):
                response = client.post(f"{API_BASE_URL}/clusters", headers=headers, json=payload)
                response.raise_for_status()

        CONSOLE.print(f"✅ [bold green]Request accepted![/bold green] Cluster '{name}' is now provisioning.")
        CONSOLE.print("   Run '[cyan]pyk8s cluster list[/cyan]' to check its status.")
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]Error:[/bold red] API returned status {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection or Timeout Error:[/bold red] Could not communicate with the API. ({e})")
    except SystemExit:
        # This catches the sys.exit(1) from the helper function on failure
        pass


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
    """Get the kubeconfig for a cluster and print it to stdout."""
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

# --- Team Group ---
@cli.group()
def team():
    """Manage teams."""
    pass

@team.command("create")
@click.argument("name")
def create_team(name: str):
    """Create a new team."""
    try:
        headers = get_auth_headers()
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(f"{API_BASE_URL}/teams", headers=headers, json={"name": name})
            response.raise_for_status()
        CONSOLE.print(f"✅ [bold green]Team '{name}' created successfully![/bold green]")
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]Error:[/bold red] API returned status {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection Error:[/bold red] {e}")

@team.command("list")
def list_teams():
    """List all teams you are a member of."""
    try:
        headers = get_auth_headers()
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(f"{API_BASE_URL}/teams", headers=headers)
            response.raise_for_status()
        teams_data = response.json()
        table = Table(title="Your Teams")
        table.add_column("Name", style="cyan")
        table.add_column("ID", style="dim")
        for t in teams_data:
            table.add_row(t['name'], t['id'])
        CONSOLE.print(table)
    except Exception as e:
        CONSOLE.print(f"[bold red]An error occurred:[/bold red] {e}")

@team.command("members")
@click.argument("team_name")
def list_members(team_name: str):
    """List all members of a specific team."""
    try:
        headers = get_auth_headers()
        with httpx.Client(timeout=TIMEOUT) as client:
            team_id = _get_team_id_from_name(client, team_name)
            response = client.get(f"{API_BASE_URL}/teams/{team_id}", headers=headers)
            response.raise_for_status()
        
        team_details = response.json()
        table = Table(title=f"Members of {team_name}")
        table.add_column("Email", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("User ID", style="dim")

        for member in team_details.get('members', []):
            table.add_row(member['email'], member['role'], member['id'])
        CONSOLE.print(table)
    except Exception as e:
        CONSOLE.print(f"[bold red]An error occurred:[/bold red] {e}")

@team.command("invite")
@click.argument("email")
@click.option("--team-name", required=True, help="The name of the team to invite the user to.")
@click.option("--role", type=click.Choice(['admin', 'member']), default='member', help="The role for the new member.")
def invite_member(email: str, team_name: str, role: str):
    """Invite a user to a team by email."""
    try:
        headers = get_auth_headers()
        with httpx.Client(timeout=TIMEOUT) as client:
            team_id = _get_team_id_from_name(client, team_name)
            payload = {"email": email, "role": role}
            
            with CONSOLE.status(f"[bold green]Inviting {email} to {team_name}...[/bold green]"):
                response = client.post(f"{API_BASE_URL}/teams/{team_id}/members", headers=headers, json=payload)
                response.raise_for_status()
        
        CONSOLE.print(f"✅ [bold green]Successfully invited {email} to the '{team_name}' team as a(n) {role}.[/bold green]")
    except httpx.HTTPStatusError as e:
        CONSOLE.print(f"[bold red]Error:[/bold red] API returned status {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
    except httpx.RequestError as e:
        CONSOLE.print(f"[bold red]Connection Error:[/bold red] {e}")


if __name__ == "__main__":
    cli.add_command(auth)
    cli.add_command(cluster)
    cli.add_command(team)
    cli()