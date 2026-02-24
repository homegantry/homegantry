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

MEMORY_PATH = os.environ.get("GANTRY_MEMORY_PATH", "/workspace/MEMORY.md")


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
        data = json.loads(resp.read().decode())
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


import json
import time
import os
import urllib.request
import urllib.error
import ssl

# News RSS feeds
RSS_FEEDS = {
    "dutch-politics": [
        "https://nos.nl/feed",
        "https://nu.nl/rss",
    ],
    "ai-news": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
    ],
}

def fetch_rss(feed_url):
    """Fetch and parse RSS feed."""
    articles = []
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Gantry/1.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        data = resp.read().decode('utf-8', errors='ignore')
        
        # Simple RSS parsing
        import re
        # Extract titles
        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', data, re.DOTALL)
        if not titles:
            titles = re.findall(r'<title>([^<]+)</title>', data)
        # Extract links
        links = re.findall(r'<link><!\[CDATA\[(.*?)\]\]></link>', data, re.DOTALL)
        if not links:
            links = re.findall(r'<link>([^<]+)</link>', data)
        
        # Clean titles (skip first which is usually feed title)
        titles = titles[1:6] if len(titles) > 1 else titles[:5]
        links = links[1:6] if len(links) > 1 else links[:5]
        
        for i, title in enumerate(titles):
            title = title.strip()
            if title and not title.startswith('<?xml'):
                articles.append({
                    "title": title,
                    "url": links[i].strip() if i < len(links) else "",
                    "source": feed_url.split('/')[2].split('.')[0].capitalize(),
                    "published": time.strftime("%d %b")
                })
    except Exception as e:
        print(f"Error fetching {feed_url}: {e}")
    return articles

def update_news():
    """Update news from RSS feeds."""
    global NEWS_DATA
    for topic, feeds in RSS_FEEDS.items():
        all_articles = []
        for feed in feeds:
            articles = fetch_rss(feed)
            all_articles.extend(articles)
        # Deduplicate by title
        seen = set()
        unique = []
        for a in all_articles:
            if a['title'] not in seen:
                seen.add(a['title'])
                unique.append(a)
        NEWS_DATA[topic] = {
            "articles": unique[:10],
            "last_updated": int(time.time())
        }

# News storage
NEWS_DATA = {
    "dutch-politics": {"articles": [], "last_updated": None},
    "ai-news": {"articles": [], "last_updated": None},
}

# Initial fetch
update_news()

# Kanban board (persistent)
KANBAN_FILE = "/workspace/kanban.json"
FALLBACK_KANBAN_FILE = "/home/g/kanban.json"

def load_kanban():
    """Load kanban data from file or use defaults."""
    import json
    default = {
        "backlog": [
            {"id": "kb-1", "title": "News article fetching", "type": "feature", "source": "ai", "created": int(time.time())},
            {"id": "kb-2", "title": "Settings page with config", "type": "feature", "source": "ai", "created": int(time.time())},
        ],
        "in_progress": [
            {"id": "kb-6", "title": "Hamburger menu overlaps title on mobile", "type": "bug", "source": "gerald", "created": int(time.time())},
            {"id": "kb-7", "title": "Logs page stays empty", "type": "bug", "source": "gerald", "created": int(time.time())},
        ],
        "done": [
            {"id": "kb-3", "title": "Kanban board", "type": "feature", "source": "ai", "created": int(time.time())},
            {"id": "kb-4", "title": "Lighter theme", "type": "feature", "source": "ai", "created": int(time.time())},
            {"id": "kb-5", "title": "Mobile sidebar", "type": "feature", "source": "ai", "created": int(time.time())},
        ],
    }
    for f in [KANBAN_FILE, FALLBACK_KANBAN_FILE]:
        try:
            if os.path.exists(f):
                with open(f, 'r') as fp:
                    return json.load(fp)
        except Exception:
            pass
    return default

def save_kanban(data):
    """Save kanban data to file."""
    import json
    # Save to both locations
    for f in [KANBAN_FILE, FALLBACK_KANBAN_FILE]:
        try:
            os.makedirs(os.path.dirname(f), exist_ok=True)
            with open(f, 'w') as fp:
                json.dump(data, fp, indent=2)
        except Exception:
            pass

KANBAN_DATA = load_kanban()


@app.get("/api/kanban")
def get_kanban():
    """Get all kanban columns and cards."""
    return {
        "columns": [
            {"id": "backlog", "name": "Backlog", "cards": KANBAN_DATA.get("backlog", [])},
            {"id": "in_progress", "name": "In Progress", "cards": KANBAN_DATA.get("in_progress", [])},
            {"id": "done", "name": "Done", "cards": KANBAN_DATA.get("done", [])},
        ],
        "ts": int(time.time()),
    }


@app.post("/api/kanban")
def add_kanban_card():
    """Add a new card to kanban."""
    import json
    
    # Read body from request
    try:
        body = json.loads(open('/dev/stdin').read()) if not hasattr(add_kanban_card, 'request') else {}
    except:
        body = {}
    
    # For now, just return success - cron can write directly to file
    return {"status": "ok", "message": "Use file /workspace/kanban.json to update"}


@app.post("/api/kanban/add")
def add_kanban_card2(title: str, col: str = "backlog", card_type: str = "feature", source: str = "ai"):
    """Add a card to a column."""
    import json
    
    card = {
        "id": f"kb-{int(time.time())}",
        "title": title,
        "type": card_type,
        "source": source,
        "created": int(time.time())
    }
    
    if col not in KANBAN_DATA:
        KANBAN_DATA[col] = []
    KANBAN_DATA[col].append(card)
    save_kanban(KANBAN_DATA)
    
    return {"status": "ok", "card": card}


@app.get("/api/openclaw")
def get_openclaw_status():
    """Get OpenClaw gateway status and stats."""
    import socket
    
    gateway_url = os.environ.get("OPENCLAW_GATEWAY_URL", "http://localhost:8080")
    
    try:
        # Try to reach the gateway
        parsed = urllib.parse.urlparse(gateway_url)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((parsed.hostname or "localhost", parsed.port or 8080))
        sock.close()
        reachable = result == 0
    except Exception:
        reachable = False
    
    return {
        "gateway_reachable": reachable,
        "gateway_url": gateway_url,
        "ts": int(time.time()),
    }


@app.post("/api/news/refresh")
def refresh_news():
    """Force refresh news from RSS feeds."""
    update_news()
    return {"status": "ok", "ts": int(time.time())}


@app.get("/api/news")
def get_news():
    """Get all news topics and their articles."""
    return {
        "topics": [
            {"id": "dutch-politics", "name": "Dutch Politics", "count": len(NEWS_DATA["dutch-politics"]["articles"])},
            {"id": "ai-news", "name": "AI News", "count": len(NEWS_DATA["ai-news"]["articles"])},
        ],
        "ts": int(time.time()),
    }


@app.get("/api/news/{topic}")
def get_news_topic(topic):
    """Get articles for a specific topic."""
    if topic not in NEWS_DATA:
        return {"error": "Topic not found", "articles": [], "ts": int(time.time())}
    return {
        "topic": topic,
        "name": topic.replace("-", " ").title(),
        "articles": NEWS_DATA[topic]["articles"][:20],
        "last_updated": NEWS_DATA[topic]["last_updated"],
        "ts": int(time.time()),
    }


@app.post("/api/news/{topic}")
def update_news_topic(topic):
    """Update news for a topic (called by cron or manually)."""
    if topic not in NEWS_DATA:
        return {"error": "Topic not found", "ts": int(time.time())}
    
    # For now, just return the current state (news fetching would be done externally)
    return {
        "topic": topic,
        "updated": True,
        "ts": int(time.time()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
