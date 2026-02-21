from fastapi import FastAPI
from pathlib import Path
import psutil
import docker
import subprocess
import os
import time

app = FastAPI()

try:
    client = docker.from_env()
except Exception:
    client = None

MEMORY_PATH = os.environ.get("GANTRY_MEMORY_PATH", str(Path.home() / ".claude/projects/-home-g-git-homegantry/memory/MEMORY.md"))


@app.get("/api/status")
def get_status():
    return {
        "system": {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage("/").percent,
            "net_sent": psutil.net_io_counters().bytes_sent,
            "net_recv": psutil.net_io_counters().bytes_recv,
            "uptime": int(time.time() - psutil.boot_time()),
            "load_avg": list(os.getloadavg()),
        },
        "gantry": {
            "status": "online",
            "version": "2026.2.21-1"
        }
    }


@app.get("/api/containers")
def get_containers():
    if not client:
        return {"error": "Docker not accessible"}
    containers = []
    for c in client.containers.list(all=True):
        containers.append({
            "name": c.name,
            "status": c.status,
            "image": c.image.tags[0] if c.image.tags else c.short_id,
        })
    return containers


@app.get("/api/core-logic")
def get_core_logic():
    """Active Claude Code / OpenClaw sessions and thinking status."""
    sessions = []

    # Detect active Claude Code processes
    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])
            if "claude" in cmdline.lower() and proc.info["pid"] != os.getpid():
                elapsed = int(time.time() - proc.info["create_time"])
                sessions.append({
                    "pid": proc.info["pid"],
                    "label": "Claude Code Session",
                    "uptime_s": elapsed,
                    "cmd_hint": cmdline[:120],
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Detect tmux sessions (common OpenClaw host)
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}:#{session_windows}:#{session_activity}"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                parts = line.split(":")
                if len(parts) >= 3:
                    sessions.append({
                        "pid": None,
                        "label": f"tmux/{parts[0]}",
                        "windows": int(parts[1]),
                        "last_activity": int(parts[2]),
                    })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return {
        "sessions": sessions,
        "thinking": "IDLE" if not sessions else "ACTIVE",
        "session_count": len(sessions),
        "ts": int(time.time()),
    }


@app.get("/api/scheduled-ops")
def get_scheduled_ops():
    """List configured cron jobs for the current user and system."""
    jobs = []

    # User crontab
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    jobs.append({"source": "user", "entry": line})
                elif line.startswith("#") and not line.startswith("# "):
                    # Commented-out job - still show it as disabled
                    jobs.append({"source": "user", "entry": line, "disabled": True})
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Systemd timers (modern cron alternative)
    try:
        result = subprocess.run(
            ["systemctl", "list-timers", "--no-pager", "--plain", "--output=short"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            for line in lines[1:]:  # skip header
                parts = line.split()
                if len(parts) >= 5 and ".timer" in line:
                    unit = next((p for p in parts if ".timer" in p), None)
                    if unit:
                        jobs.append({"source": "systemd", "entry": unit})
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return {"jobs": jobs, "count": len(jobs), "ts": int(time.time())}


@app.get("/api/memory")
def get_memory():
    """Read recent architectural memory from MEMORY.md."""
    path = Path(MEMORY_PATH)
    if not path.exists():
        return {"exists": False, "lines": [], "snippet": "[ NO MEMORY FILE FOUND ]"}

    try:
        text = path.read_text(encoding="utf-8")
        lines = text.strip().splitlines()
        # Return last 30 meaningful lines for the dashboard snippet
        meaningful = [l for l in lines if l.strip()]
        recent = meaningful[-30:] if len(meaningful) > 30 else meaningful
        return {
            "exists": True,
            "total_lines": len(lines),
            "lines": recent,
            "snippet": "\n".join(recent),
        }
    except Exception as e:
        return {"exists": False, "lines": [], "snippet": f"[ READ ERROR: {e} ]"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
