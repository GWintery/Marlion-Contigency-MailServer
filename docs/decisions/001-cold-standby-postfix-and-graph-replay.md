# ADR-001: Cold-Standby Receive-Only Postfix, Localhost OTP UI & MX-Guarded Graph Replay

- **Status:** `Accepted`
- **Date:** 2026-11-16 (Seeded from verified VPS configs & runbook)
- **Scope:** Mail Failover / Security / Microsoft Graph Replay

## Imperative Rule
1. **Cold Standby by Default:** Keep `postfix`, `otp-mail-ui.service`, UFW `25/tcp`, Tencent Lighthouse `TCP:25`, and Entra `VPS-Mail-Recovery` sign-in **disabled** outside active Microsoft 365 outages.
2. **Receive-Only Postfix:** Keep `default_transport = error:Outbound mail disabled`, `relay_transport = error:Relay disabled`, `smtpd_tls_protocols = >=TLSv1.2`, and `disable_vrfy_command = yes` in `vps/postfix/main.cf`.
3. **Localhost-Only Web UI:** Keep `otp-mail-ui.py` bound exclusively to `127.0.0.1:8025` (SSH tunnel only), running under non-login user `otpmail` with `html.escape()` and `<iframe sandbox='' srcdoc=...>`.
4. **Loop-Safe Graph Replay:** Never run `replay-otp-mail --send` until `1.1.1.1` confirms MX records for `marlion.co.id` and `manorian.co.id` point back to `outlook.com` (`check_mx_reverted()`), using chunked `uploadSession` above `2,500,000` bytes.

## Rejected / Forbidden Alternatives
- **Do NOT run an open 24/7 mail server on `43.134.92.151`**: exposes port 25 to spam/scanner abuse and wastes 2 GB VPS RAM.
- **Do NOT bind `otp-mail-ui.py` to `0.0.0.0` or proxy it publicly via Nginx**: unauthenticated email/OTP exposure.
- **Do NOT enable outbound SMTP sending on Postfix**: would turn the VPS into a relay target and cause reputation/deliverability issues.

## Context & Trade-Offs (Source-Verified)
- Verified directly from VPS `/etc/postfix/main.cf`, `/etc/postfix/virtual`, `/etc/systemd/system/otp-mail-ui.service`, `/usr/local/bin/read-otp-mail`, `/usr/local/bin/otp-mail-ui.py`, `/usr/local/bin/replay-otp-mail`, and `docs/MAIL_DISASTER_RECOVERY.md`.

## Files & Configs Affected
- `vps/postfix/main.cf`, `vps/postfix/virtual`
- `vps/systemd/otp-mail-ui.service`
- `vps/bin/read-otp-mail`, `vps/bin/otp-mail-ui.py`, `vps/bin/replay-otp-mail`
- `docs/MAIL_DISASTER_RECOVERY.md`

## Verification
- Confirm `ss -tlnp` on VPS shows neither `:25` nor `:8025` listening during Cold Standby, and `Test-NetConnection -ComputerName 43.134.92.151 -Port 25` returns `TcpTestSucceeded : False`.
