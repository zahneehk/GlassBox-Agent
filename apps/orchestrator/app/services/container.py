"""GlassBox Orchestrator — Container lifecycle management via Docker SDK."""
import asyncio
import docker
from docker.errors import NotFound, APIError

from app.core.config import settings

_client = None


def get_docker_client():
    global _client
    if _client is None:
        _client = docker.from_env()
    return _client


class ContainerManager:
    """Manages Docker containers for Runner instances."""

    def __init__(self):
        self._port_counter = settings.novnc_port_start

    def _next_ports(self) -> dict:
        """Allocate next available port set for a container."""
        novnc = self._port_counter
        vnc = settings.vnc_port_start + (novnc - settings.novnc_port_start)
        runner = settings.runner_port + (novnc - settings.novnc_port_start)
        self._port_counter += 1
        return {"novnc": novnc, "vnc": vnc, "runner": runner}

    async def create_container(self, run_id: str) -> dict:
        """Create and start a Runner container. Returns container info dict."""
        client = get_docker_client()
        ports = self._next_ports()

        def _create():
            container = client.containers.run(
                image=settings.runner_image,
                name=f"gb-runner-{run_id[:8]}",
                detach=True,
                remove=False,
                ports={
                    f"{settings.runner_port}/tcp": ports["runner"],
                    "5900/tcp": ports["vnc"],
                    "6080/tcp": ports["novnc"],
                },
                environment={
                    "RUN_ID": run_id,
                    "RUNNER_PORT": str(settings.runner_port),
                    "VNC_PORT": "5900",
                    "NOVNC_PORT": "6080",
                    "SCREEN_RESOLUTION": "1280x720x24",
                },
                mem_limit=settings.container_memory_limit,
                cpu_quota=int(settings.container_cpu_limit * 100000),
                labels={"glassbox.run_id": run_id, "glassbox.role": "runner"},
            )
            container.reload()
            ip = None
            networks = container.attrs.get("NetworkSettings", {}).get("Networks", {})
            for net in networks.values():
                ip = net.get("IPAddress")
                if ip:
                    break
            return {
                "container_id": container.id[:12],
                "container_ip": ip,
                "novnc_port": ports["novnc"],
                "vnc_port": ports["vnc"],
                "runner_port": ports["runner"],
            }

        return await asyncio.to_thread(_create)

    async def destroy_container(self, container_id: str) -> bool:
        """Stop and remove a container."""
        client = get_docker_client()

        def _destroy():
            try:
                container = client.containers.get(container_id)
                container.stop(timeout=5)
                container.remove(force=True)
                return True
            except NotFound:
                return False
            except APIError as e:
                print(f"[ContainerManager] destroy error: {e}")
                return False

        return await asyncio.to_thread(_destroy)

    async def get_container_status(self, container_id: str) -> str | None:
        """Get container status string or None if not found."""
        client = get_docker_client()

        def _status():
            try:
                container = client.containers.get(container_id)
                return container.status
            except NotFound:
                return None

        return await asyncio.to_thread(_status)


container_manager = ContainerManager()
