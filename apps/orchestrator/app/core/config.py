"""GlassBox Orchestrator — Core configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://glassbox:glassbox@localhost:5432/glassbox"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Docker
    runner_image: str = "glassbox-runner:latest"
    runner_network: str = "glassbox-net"
    container_memory_limit: str = "1g"
    container_cpu_limit: float = 1.0

    # HITL
    hitl_timeout_seconds: int = 300  # 5 min default

    # Runner
    runner_port: int = 3001
    novnc_port_start: int = 6080
    vnc_port_start: int = 5900

    class Config:
        env_prefix = "GB_"
        env_file = ".env"


settings = Settings()
