# Marlion Emergency Mail Recovery — Living Project Context

> **Purpose:** Persistent cross-conversation context ledger for the Cold-Standby Emergency Mail DR system (`43.134.92.151`). Every new conversation reads this file and `docs/decisions/` before planning or editing, and updates it before closing a change.

---

## 1. Project Identity, Live Status & Inventory
- **GitHub Repository:** `https://github.com/GWintery/Marlion-Contigency-MailServer` (`main` + `dev` branch flow)
- **VPS State:** **Cold Standby** on Tencent Cloud Lighthouse (`43.134.92.151`, Ubuntu 24.04 + CloudPanel v2, shared with `apps.marlion.co.id` and future `manorian.co.id`).
- **MX Failover Hostname:** `apps.marlion.co.id` (Cloudflare DNS-only gray cloud, reuses CloudPanel TLS cert `/etc/nginx/ssl-certificates/apps.marlion.co.id.{crt,key}`).
- **Entra ID Public Client App:** `VPS-Mail-Recovery` (Tenant `a61c465d-eaa8-406d-aeca-f732d2a826a9`, App `31dd65fa-71ba-40e2-bf58-934a02894635`, delegated `Mail.Send` + `Mail.ReadWrite` + `offline_access`; Enterprise App sign-in kept **No** during Cold Standby).
- **Mirrored VPS Files (`vps/`):**
  - `vps/postfix/main.cf` & `vps/postfix/virtual`
  - `vps/systemd/otp-mail-ui.service` (`User=otpmail`, `NoNewPrivileges=yes`, `PrivateTmp=yes`)
  - `vps/bin/read-otp-mail` (CLI OTP extractor)
  - `vps/bin/otp-mail-ui.py` (Read-only `127.0.0.1:8025` inbox UI)
  - `vps/bin/replay-otp-mail` (Microsoft Graph replay with `sendMail` <= 2.5 MB / `uploadSession` chunked upload > 2.5 MB, MX loop guard, and `replayed.log` resume)

---

## 2. Active Decisions Index (Do Not Silently Override)
| ADR | Status | Rule Summary | Key Files |
| :--- | :--- | :--- | :--- |
| [ADR-001](decisions/001-cold-standby-postfix-and-graph-replay.md) | `Accepted` | Keep Postfix receive-only & disabled outside outages; localhost-only OTP UI (`127.0.0.1:8025`); Graph Device Code replay only after MX revert | `vps/postfix/main.cf`, `vps/bin/otp-mail-ui.py`, `vps/bin/replay-otp-mail`, `docs/MAIL_DISASTER_RECOVERY.md` |

---

## 3. Recent Feature Handoffs
- **2026-11-16 — Extracted Standalone Repository & Synced VPS Source Backup**
  - Separated Emergency Mail DR out of `Manorian-Website` into standalone repo `G:\Projects\marlion-mail-recovery`.
  - Pulled exact live VPS scripts & Postfix/systemd configs via SSH/SCP into `vps/` (audited: zero secrets/tokens/Maildir data included), moved `MAIL_DISASTER_RECOVERY.md` into `docs/`, and seeded `AGENTS.md`, `docs/CONTEXT.md`, and `ADR-001`.
