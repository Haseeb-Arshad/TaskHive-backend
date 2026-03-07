# TaskHive API — DigitalOcean Droplet Deployment Guide

## One-time setup (first deploy)

### 1. Clone the repo

```bash
mkdir -p /opt/taskhive
cd /opt/taskhive
git clone git@github.com:Haseeb-Arshad/TaskHive-backend.git repo
cd repo
```

### 2. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### 3. Create venv and install dependencies

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

### 4. Create .env

```bash
cp .env.example .env
nano .env
```

Fill in all values — the critical ones:

```
DATABASE_URL=postgresql+asyncpg://postgres:Haseebarshad123@db.qpdszbmoqxkytvrsbtsh.supabase.co:5432/postgres
CORS_ORIGINS=https://task-hive-sigma.vercel.app,http://localhost:3000
ENVIRONMENT=production
NEXT_APP_URL=https://task-hive-sigma.vercel.app
TASKHIVE_API_BASE_URL=https://task-hive-sigma.vercel.app/api/v1
TASKHIVE_API_KEY=th_agent_4c4f3cab5cbc247ea17f489b71e3f963318c99590e57540bb883dd0a1bfd4006
WORKSPACE_ROOT=/opt/taskhive/workspaces
AGENT_WORKSPACE_DIR=/opt/taskhive/agent_works
```

### 5. Create required directories

```bash
mkdir -p /opt/taskhive/workspaces /opt/taskhive/agent_works
```

### 6. Enable IPv6 (required — Supabase direct connection is IPv6 only)

**In DigitalOcean control panel:**
- Droplets → your droplet → Settings → Networking → IPv6 → Enable
- Note your **IPv6 address** and **IPv6 gateway** shown on that page
- Power the droplet back on

**On the droplet — configure netplan:**

```bash
sudo cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.bak
sudo python3 scripts/enable_ipv6_netplan.py
sudo netplan apply
```

> Edit `scripts/enable_ipv6_netplan.py` first if your IPv6 address/gateway differ from what's hardcoded.

**Lock the config so cloud-init doesn't reset it on reboot:**

```bash
echo 'network: {config: disabled}' | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
```

**Verify IPv6 works:**

```bash
ping6 -c 3 2001:4860:4860::8888
```

### 7. Test the database connection

```bash
.venv/bin/python3 scripts/find_working_connection.py
```

### 8. Run migrations

```bash
.venv/bin/alembic upgrade head
```

### 9. Install systemd service

```bash
sudo cp /opt/taskhive/repo/scripts/taskhive-api.service /etc/systemd/system/taskhive-api.service
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now taskhive-api
sudo systemctl status taskhive-api
```

---

## Every future deploy (git push -> droplet update)

```bash
cd /opt/taskhive/repo
git pull origin main
uv pip install -e .
.venv/bin/alembic upgrade head
sudo systemctl daemon-reload
sudo systemctl restart taskhive-api taskhive-swarm taskhive-worker
sudo systemctl status taskhive-api
sudo systemctl status taskhive-swarm
sudo systemctl status taskhive-worker
```

### Verify deploy env for swarm/worker (required for Vercel deploys)

```bash
cd /opt/taskhive/repo
grep -E '^(VERCEL_TOKEN|VERCEL_ORG_ID|VERCEL_PROJECT_ID)=' .env
sudo systemctl show taskhive-swarm --property=Environment
sudo systemctl show taskhive-worker --property=Environment
```

If Vercel still fails from the agent:

```bash
sudo journalctl -u taskhive-swarm -n 150 --no-pager
sudo journalctl -u taskhive-worker -n 150 --no-pager
```

---

## Useful commands

```bash
# Live logs
sudo journalctl -u taskhive-api -f

# Restart service
sudo systemctl restart taskhive-api

# Stop service
sudo systemctl stop taskhive-api

# Check service status
sudo systemctl status taskhive-api

# Test DB connection
cd /opt/taskhive/repo && .venv/bin/python3 scripts/find_working_connection.py

# Open firewall for port 8000
ufw allow 8000/tcp
```

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Network is unreachable` | IPv6 not enabled — follow Step 6 |
| `Tenant or user not found` | Using pooler URL instead of direct — use `db.PROJECT.supabase.co:5432` |
| `Could not parse SQLAlchemy URL` | Duplicate `DATABASE_URL=` key or spaces in URL — check with `grep DATABASE_URL .env \| cat -A` |
| `No module named 'app'` | Wrong Python — use `.venv/bin/alembic`, not system `alembic` |
| `alembic: command not found` | Venv not installed — run `uv pip install -e .` |
| Service not starting | Check logs: `sudo journalctl -u taskhive-api -n 50` |
| Vercel deploy fails from agent | Ensure `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` are in `/opt/taskhive/repo/.env`, then restart `taskhive-swarm` and `taskhive-worker` |
| IPv6 lost after reboot | Run the cloud-init disable command in Step 6 |

