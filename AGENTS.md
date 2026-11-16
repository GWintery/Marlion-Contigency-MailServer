# Marlion Emergency Mail Recovery (`AGENTS.md`)

Cold-standby M365 email outage failover & Graph replay toolkit for `marlion.co.id` & `manorian.co.id` on VPS `43.134.92.151`.
- **Sibling Projects (`G:\Projects\`)**: `manorian-website` (`manorian.co.id`) and `marlion-ops-pwa` (`apps.marlion.co.id`).

## Mandatory Session Startup & Wrap-Up
1. **Before planning or editing**: Read `docs/CONTEXT.md`, `docs/MAIL_DISASTER_RECOVERY.md`, and relevant ADRs in `docs/decisions/`.
2. **Verify from source first**: Inspect `vps/postfix/*`, `vps/systemd/*`, `vps/bin/*`, and official Microsoft Graph / Postfix docs before recommending changes.
3. **Before wrapping up a feature**: Invoke `decision-ledger` to update `docs/CONTEXT.md` and record/supersede an ADR if any security, MX, or replay behavior changed.

## Always Do
- Keep `vps/` scripts with LF line endings (`\n`) so they execute cleanly on Ubuntu 24.04.
- Keep `otp-mail-ui.py` bound strictly to `127.0.0.1:8025` (SSH tunnel access only) with HTML escaping and `<iframe sandbox='' ...>`.
- Require MX reversion verification (`check_mx_reverted()` on `1.1.1.1`) before any `--send` Graph replay.

## Ask First
- Before modifying `/etc/postfix/main.cf`, `/etc/postfix/virtual`, UFW/Lighthouse TCP port 25 rules, or Entra ID app `VPS-Mail-Recovery`.
- Before changing `replay-otp-mail` Graph scopes, recipient extraction, or `replayed.log` idempotency behavior.

## Never Do
- **Never leave TCP port 25, `postfix`, or `otp-mail-ui.service` running outside an active M365 outage** (must return to Cold Standby with wiped Maildir).
- **Never bind `otp-mail-ui.py` to `0.0.0.0`** or expose port `8025` publicly.
- **Never enable outbound SMTP relay on Postfix** (`default_transport = error:...` and `relay_transport = error:...` must remain disabled).
- **Never commit captured `.eml` files, `Maildir/`, `replayed.log`, SSH keys, or OAuth tokens** to Git.
