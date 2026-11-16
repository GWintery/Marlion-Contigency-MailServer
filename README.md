# Marlion Emergency Mail Recovery (`marlion-mail-recovery`)

Cold-standby inbound email failover & Microsoft 365 Exchange Online replay toolkit for **`marlion.co.id`** and **`manorian.co.id`**, hosted on Tencent Cloud Lighthouse (`43.134.92.151`, Ubuntu 24.04).

## Architecture Overview
- **Normal State (Cold Standby):** `postfix` and `otp-mail-ui.service` are disabled, and TCP port `25` is closed on both UFW and Tencent Lighthouse Firewall.
- **Outage Failover:** Temporarily enables Postfix receive-only catch-all (`default_transport = error:Outbound mail disabled`, `relay_transport = error:Relay disabled`) + localhost-only web OTP viewer (`127.0.0.1:8025` over SSH tunnel) + CLI reader (`read-otp-mail`).
- **Recovery Replay:** After restoring Outlook MX records and confirming DNS drain, `replay-otp-mail` authenticates via Entra ID Device Code Flow (`VPS-Mail-Recovery`) and replays `.eml` attachments back into M365 via Microsoft Graph before returning the VPS to zero-open-ports Cold Standby.

## Repository Structure
```text
├── AGENTS.md                           # AI agent anchor rules & security boundaries
├── docs/
│   ├── MAIL_DISASTER_RECOVERY.md       # Full 4-phase emergency failover & replay runbook
│   ├── CONTEXT.md                      # Living context & active decisions index
│   └── decisions/                      # Architecture Decision Records (ADRs)
└── vps/
    ├── postfix/
    │   ├── main.cf                     # Mirror of /etc/postfix/main.cf
    │   └── virtual                     # Mirror of /etc/postfix/virtual
    ├── systemd/
    │   └── otp-mail-ui.service         # Mirror of /etc/systemd/system/otp-mail-ui.service
    └── bin/
        ├── read-otp-mail               # Mirror of /usr/local/bin/read-otp-mail
        ├── otp-mail-ui.py              # Mirror of /usr/local/bin/otp-mail-ui.py
        └── replay-otp-mail             # Mirror of /usr/local/bin/replay-otp-mail
```

See [docs/MAIL_DISASTER_RECOVERY.md](docs/MAIL_DISASTER_RECOVERY.md) for step-by-step activation and recovery commands.
