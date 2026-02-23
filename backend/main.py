from fastapi import FastAPI
from pathlib import Path
import psutil
import docker
import subprocess
import os
import time
import re
import urllib.request
import urllib.error
import json

app = FastAPI()

try:
    client = docker.from_env()
except Exception:
    client = None

MEMORY_PATH = os.environ.get("GANTRY_MEMORY_PATH", "/home/g/.openclaw/workspace/MEMORY.md")


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


@app.get("/api/logs")
def get_logs():
    """Return the last 100 lines of system/application logs."""
    entries = []

    # Try journalctl first (systemd-based systems)
    try:
        result = subprocess.run(
            ["journalctl", "--user", "--no-pager", "-n", "100", "-o", "json"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            import json as _json
            for line in result.stdout.strip().splitlines():
                try:
                    obj = _json.loads(line)
                    ts = int(obj.get("__REALTIME_TIMESTAMP", "0")) // 1_000_000
                    priority = int(obj.get("PRIORITY", 6))
                    level = {0: "EMERG", 1: "ALERT", 2: "CRIT", 3: "ERROR",
                             4: "WARN", 5: "NOTICE", 6: "INFO", 7: "DEBUG"}.get(priority, "INFO")
                    msg = obj.get("MESSAGE", "")
                    unit = obj.get("_SYSTEMD_UNIT", obj.get("SYSLOG_IDENTIFIER", ""))
                    entries.append({"timestamp": ts, "level": level, "message": f"[{unit}] {msg}" if unit else msg})
                except (_json.JSONDecodeError, ValueError):
                    continue
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: try system journal without --user flag
    if not entries:
        try:
            result = subprocess.run(
                ["journalctl", "--no-pager", "-n", "100", "-o", "short-iso"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    # Parse short-iso format: "2026-02-21T10:30:00+0000 host unit[pid]: message"
                    match = re.match(r"^(\S+)\s+\S+\s+(\S+?)(?:\[\d+\])?:\s+(.*)", line)
                    if match:
                        ts_str, unit, msg = match.groups()
                        try:
                            from datetime import datetime, timezone
                            dt = datetime.fromisoformat(ts_str.replace("+0000", "+00:00"))
                            ts = int(dt.timestamp())
                        except Exception:
                            ts = int(time.time())
                        entries.append({"timestamp": ts, "level": "INFO", "message": f"[{unit}] {msg}"})
                    elif line.strip():
                        entries.append({"timestamp": int(time.time()), "level": "INFO", "message": line.strip()})
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # Fallback: try /var/log/syslog
    if not entries:
        try:
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/syslog"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    entries.append({"timestamp": int(time.time()), "level": "INFO", "message": line.strip()})
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return entries[-100:]


@app.get("/api/gateway-status")
def get_gateway_status():
    """Check if the OpenClaw gateway is reachable."""
    gateway_url = os.environ.get("OPENCLAW_GATEWAY_URL", "http://localhost:8080")
    try:
        req = urllib.request.Request(gateway_url, method="HEAD")
        resp = urllib.request.urlopen(req, timeout=3)
        return {
            "reachable": True,
            "status_code": resp.status,
            "url": gateway_url,
            "ts": int(time.time()),
        }
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return {
            "reachable": False,
            "error": str(e),
            "url": gateway_url,
            "ts": int(time.time()),
        }


@app.get("/api/weather")
def get_weather():
    """Get current weather for Amsterdam, NL."""
    try:
        url = "https://wttr.in/Amsterdam?format=j1"
        resp = urllib.request.urlopen(url, timeout=10)
        data = _json.loads(resp.read().decode())
        current = data["current_condition"][0]
        return {
            "location": "Amsterdam, NL",
            "temp_C": int(current["temp_C"]),
            "condition": current["weatherDesc"][0]["value"],
            "humidity": int(current["humidity"]),
            "wind_kmh": int(current["windspeedKmph"]),
            "feels_C": int(current["FeelsLikeC"]),
            "ts": int(time.time()),
        }
    except Exception as e:
        return {"error": str(e), "ts": int(time.time())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
