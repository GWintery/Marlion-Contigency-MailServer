#!/usr/bin/env python3
import email
from email import policy
import glob
import html
import os
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse

MAIL_DIRS = ["/home/otpmail/Maildir/new", "/home/otpmail/Maildir/cur"]


def list_emails(limit=50):
    files = []
    for d in MAIL_DIRS:
        if os.path.isdir(d):
            files.extend(glob.glob(os.path.join(d, "*")))
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:limit]


def find_email_path(file_id):
    if not file_id or "/" in file_id or "\\" in file_id or ".." in file_id:
        return None
    for d in MAIL_DIRS:
        candidate = os.path.join(d, os.path.basename(file_id))
        if os.path.isfile(candidate):
            return candidate
    return None


def extract_bodies(msg):
    plain_text = ""
    html_body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get_content_disposition() or "")
            if "attachment" in disp:
                continue
            try:
                content = part.get_content()
            except Exception:
                payload = part.get_payload(decode=True)
                content = payload.decode("utf-8", errors="replace") if payload else ""
            if not isinstance(content, str):
                continue
            if ctype == "text/plain" and not plain_text:
                plain_text = content
            elif ctype == "text/html" and not html_body:
                html_body = content
    else:
        ctype = msg.get_content_type()
        try:
            content = msg.get_content()
        except Exception:
            payload = msg.get_payload(decode=True)
            content = payload.decode("utf-8", errors="replace") if payload else ""
        if isinstance(content, str):
            if ctype == "text/html":
                html_body = content
            else:
                plain_text = content
    return plain_text, html_body


def parse_meta(path):
    with open(path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
    orig_to = str(msg.get("X-Original-To") or msg.get("Delivered-To") or msg.get("To", ""))
    frm = str(msg.get("From", ""))
    subj = str(msg.get("Subject", "(no subject)"))
    plain_text, html_body = extract_bodies(msg)
    searchable = plain_text or re.sub(r"<[^>]+>", " ", html_body)
    searchable = re.sub(r"\s+", " ", f"{subj} {searchable}").strip()
    codes = list(dict.fromkeys(re.findall(r"\b\d{4,8}\b", searchable)))[:6]
    return {
        "id": os.path.basename(path),
        "time": mtime,
        "from": frm,
        "to": orig_to,
        "subject": subj,
        "codes": codes,
        "plain": plain_text,
        "html": html_body,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path not in ("/", "/index.html"):
            self.send_error(404)
            return

        qs = parse_qs(parsed.query)
        selected_id = qs.get("id", [None])[0]
        paths = list_emails()
        items = []
        for p in paths:
            try:
                items.append(parse_meta(p))
            except Exception:
                continue

        selected = None
        if selected_id:
            sp = find_email_path(selected_id)
            if sp:
                selected = parse_meta(sp)
        elif items:
            selected = items[0]

        rows_html = []
        for it in items:
            active = "active" if selected and it["id"] == selected["id"] else ""
            badges = " ".join(f"<span class='code'>{html.escape(c)}</span>" for c in it["codes"][:2])
            rows_html.append(
                f"<a class='item {active}' href='/?id={quote(it['id'], safe='')}'>"
                f"<div class='meta'>{html.escape(it['time'])} &bull; To: <b>{html.escape(it['to'])}</b></div>"
                f"<div class='subj'>{html.escape(it['subject'])} {badges}</div>"
                f"<div class='from'>From: {html.escape(it['from'])}</div>"
                f"</a>"
            )

        if selected:
            code_pills = " ".join(f"<span class='code big'>{html.escape(c)}</span>" for c in selected["codes"])
            if selected["html"]:
                body_view = f"<iframe sandbox='' srcdoc='{html.escape(selected['html'], quote=True)}'></iframe>"
            else:
                body_view = f"<pre>{html.escape(selected['plain'] or '(empty body)')}</pre>"
            detail_html = (
                f"<div class='detail-head'>"
                f"<h2>{html.escape(selected['subject'])}</h2>"
                f"<div class='meta'><b>Time:</b> {html.escape(selected['time'])}<br>"
                f"<b>From:</b> {html.escape(selected['from'])}<br>"
                f"<b>To:</b> {html.escape(selected['to'])}</div>"
                f"{('<div class=\"codes-row\">Detected numbers: ' + code_pills + '</div>') if code_pills else ''}"
                f"</div>"
                f"<div class='detail-body'>{body_view}</div>"
            )
        else:
            detail_html = "<div class='empty'>No emails received in /home/otpmail/Maildir yet.</div>"

        page = f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<meta http-equiv='refresh' content='15'>
<title>Temp OTP Inbox (Local SSH Tunnel)</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; }}
  header {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; background: #1e293b; border-bottom: 1px solid #334155; }}
  header h1 {{ font-size: 16px; margin: 0; }}
  .btn {{ background: #2563eb; color: #fff; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 13px; }}
  .wrap {{ display: grid; grid-template-columns: 380px 1fr; height: calc(100vh - 49px); }}
  .list {{ border-right: 1px solid #334155; overflow-y: auto; }}
  .item {{ display: block; padding: 12px 14px; border-bottom: 1px solid #1e293b; color: inherit; text-decoration: none; }}
  .item:hover, .item.active {{ background: #1e293b; }}
  .meta {{ font-size: 12px; color: #94a3b8; margin-bottom: 4px; line-height: 1.4; }}
  .subj {{ font-size: 14px; font-weight: 600; margin-bottom: 3px; }}
  .from {{ font-size: 12px; color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .code {{ display: inline-block; background: #065f46; color: #a7f3d0; padding: 1px 6px; border-radius: 4px; font-family: monospace; font-size: 12px; margin-left: 4px; }}
  .code.big {{ font-size: 15px; padding: 3px 8px; user-select: all; }}
  .detail {{ display: flex; flex-direction: column; overflow: hidden; }}
  .detail-head {{ padding: 16px 20px; border-bottom: 1px solid #334155; background: #111827; }}
  .detail-head h2 {{ margin: 0 0 8px 0; font-size: 18px; }}
  .codes-row {{ margin-top: 10px; font-size: 13px; }}
  .detail-body {{ flex: 1; overflow: auto; background: #fff; color: #111; }}
  .detail-body iframe {{ width: 100%; height: 100%; border: 0; }}
  .detail-body pre {{ margin: 0; padding: 20px; white-space: pre-wrap; font-family: ui-monospace, monospace; font-size: 13px; }}
  .empty {{ padding: 32px; color: #94a3b8; }}
</style>
</head>
<body>
<header>
  <h1>Temp OTP Inbox &mdash; marlion.co.id &amp; manorian.co.id ({len(items)})</h1>
  <a class='btn' href='/'>Refresh (auto 15s)</a>
</header>
<div class='wrap'>
  <div class='list'>{''.join(rows_html) if rows_html else '<div class="empty">Waiting for inbound mail...</div>'}</div>
  <div class='detail'>{detail_html}</div>
</div>
</body>
</html>"""

        body_bytes = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8025), Handler).serve_forever()
