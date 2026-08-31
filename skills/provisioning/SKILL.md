---
name: provisioning
description: Checklists and procedures for provisioning new services, cron jobs, pm2 processes, and systemd units
invocation: When the user asks to set up, provision, deploy, or configure a new service, cron job, worker, or system process
---

# Provisioning Skill

Checklists and procedures for setting up new services on Matthew's Linux workstation. Follow these patterns to ensure consistency and prevent misconfigurations.

## Pre-flight Checks (Always Run First)

1. Disk space: `df -h /home /` (ensure >10% free)
2. Port conflicts: `lsof -i :<port>` (if service needs a port)
3. Existing services: `pm2 list`, `systemctl --user list-units --type=service`
4. Crontab review: `crontab -l`

## Cron Job Setup

```bash
# NEVER pipe a transform straight into `crontab -` -- if the transform errors it can
# emit empty stdout and silently wipe the whole crontab. Snapshot, edit the file,
# verify, then load it.
crontab -l > /tmp/crontab.backup.$(date +%Y%m%d-%H%M%S)
crontab -l > /tmp/crontab.edit 2>/dev/null || true
printf '\n# <description>\n<schedule> <command> >> ~/logs/<name>.log 2>&1\n' >> /tmp/crontab.edit

# Verify line count + active-job count before loading
wc -l /tmp/crontab.edit
grep -c '^[^#]' /tmp/crontab.edit

crontab /tmp/crontab.edit

# Verify
crontab -l | tail -3

# Common schedules
# Every 15 min:    */15 * * * *
# Daily 8am:       0 8 * * *
# Weekdays 10am:   0 10 * * 1-5
# Weekly Sun 8pm:  0 20 * * 0
```

**Checklist:**
- [ ] Script is executable (`chmod +x`)
- [ ] Script has `#!/usr/bin/env python3` (or appropriate shebang)
- [ ] Absolute paths used (no relative paths in cron)
- [ ] Log output redirected to `/tmp/<name>.log`
- [ ] Script loads env from `~/.env.shared` (never hardcode keys)
- [ ] Test with `--dry-run` flag before adding to cron
- [ ] Verify with `crontab -l` after adding

## PM2 Process Setup

```javascript
// Add to ecosystem.config.cjs
{
  name: '<service-name>',
  script: 'dist/<script>.js',
  args: '<any-args>',
  cwd: __dirname,
  interpreter: 'node',
  env: { NODE_ENV: 'production' },
  restart_delay: 5000,
  max_restarts: 10,
  min_uptime: 60000,
  exp_backoff_restart_delay: 1000,
}
```

**Checklist:**
- [ ] Added to `ecosystem.config.cjs` in claudeclaw project
- [ ] TypeScript compiled (`npm run build`)
- [ ] Environment variables not hardcoded (use `readEnvFile()` pattern)
- [ ] Process has restart limits (prevent rapid crash loops)
- [ ] Reload: `pm2 reload ecosystem.config.cjs`
- [ ] Verify: `pm2 list`, check status is "online"
- [ ] Save pm2 state: `pm2 save`
- [ ] Check logs: `pm2 logs <name> --lines 20`

## Systemd User Service

```ini
# ~/.config/systemd/user/<name>.service
[Unit]
Description=<Service Name>
After=network.target

[Service]
Type=simple
ExecStart=<full-path-to-command>
Restart=on-failure
RestartSec=10
Environment="PATH=/home/apexaipc/.local/bin:/usr/bin:/bin"

[Install]
WantedBy=default.target
```

**Checklist:**
- [ ] Service file created at `~/.config/systemd/user/<name>.service`
- [ ] `systemctl --user daemon-reload`
- [ ] `systemctl --user enable <name>`
- [ ] `systemctl --user start <name>`
- [ ] Verify: `systemctl --user status <name>`
- [ ] Check journal: `journalctl --user -u <name> -f`
- [ ] Ensure lingering enabled: `loginctl enable-linger apexaipc`

## Agent Seat Setup (Paperclip)

DEAD as of 2026-05-29: the `~/projects/claudeclaw` repo this section described (worker
personas, `src/db.ts` `WorkerType` union, `src/classifier.ts`/`src/scheduler.ts`
keyword routing, `ecosystem.config.cjs` pm2 entries) was retired and replaced by
CCOS/`claudeclaw-os`. Work dispatch is now Paperclip-native.

**To add a new agent seat:**

1. Create the agent directory: `mkdir -p /home/apexaipc/.paperclip/instances/default/agents/<name>/`
2. Create `AGENTS.md` with the seat's role, lane, and hard boundaries (see existing seats
   for the pattern, e.g. `agents/kup/AGENTS.md`)
3. Create `agent.yaml` alongside it with the seat's model/tool config
4. Assign issues to the new seat via the Paperclip board (owner field), not a keyword
   router or pm2 entry

## Rollback Procedures

**Cron:** `crontab -e` and delete the offending line, or comment with `#`

**PM2:** `pm2 stop <name> && pm2 delete <name> && pm2 save`

**Systemd:** `systemctl --user stop <name> && systemctl --user disable <name>`

**Git (if code was changed):** `git stash` or `git checkout -- <file>`

## Existing Services Reference

| Service | Type | Config Location |
|---------|------|-----------------|
| ea-claude | pm2 | ecosystem.config.cjs |
| ea-claude-default | pm2 | ecosystem.config.cjs |
| ea-claude-starscream | pm2 | ecosystem.config.cjs |
| metroplex | systemd | ~/.config/systemd/user/metroplex.service |
| dashboard report | cron | */30 * * * * |
| morning/evening reports | cron | 0 8/16 * * * |
| watchdog | cron | */15 * * * * |
| starscream analytics | cron | 0 18 * * * |
| research-agents | cron | see crontab |
| sky-lynx | cron | 0 2 * * 0 |
| pdf-service | pm2 | separate config |
