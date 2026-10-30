import csv
import io
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent

def load_env():
    path = ROOT / '.env'
    if not path.exists():
        return
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))

load_env()

PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aether AI Waitlist</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f6f7f1;color:#183b36;font:15px/1.5 system-ui,Segoe UI,sans-serif}.wrap{max-width:1120px;margin:48px auto;padding:0 22px}h1{font:42px/1.1 Georgia,serif;margin:8px 0}p{color:#60736d}.eyebrow{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#255f52;font-weight:700}.bar{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:28px 0 16px}.btn{display:inline-block;padding:11px 15px;border:0;border-radius:7px;background:#123d38;color:white;text-decoration:none;font-weight:700;cursor:pointer}.status{font-size:13px;color:#60736d}table{width:100%;border-collapse:collapse;background:#fffefa;border:1px solid #d9e2db;border-radius:10px;overflow:hidden}th,td{text-align:left;padding:13px 14px;border-bottom:1px solid #edf0eb;vertical-align:top}th{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#60736d;background:#f0f3ed}td{font-size:13px}tr:last-child td{border:0}.empty{padding:30px;text-align:center;color:#60736d}.error{color:#a24228}.pill{display:inline-block;border-radius:20px;padding:3px 8px;background:#e5f0e9;color:#255f52;font-size:11px;font-weight:700}@media(max-width:700px){.bar{align-items:start;flex-direction:column}table,tbody,tr,td{display:block}thead{display:none}tr{border-bottom:1px solid #d9e2db;padding:10px}td{border:0;padding:4px 2px}td:before{content:attr(data-label) ': ';font-weight:700;color:#60736d}}</style>
<div class="wrap"><span class="eyebrow">Local dashboard</span><h1>Aether AI waitlist</h1><p>Entries are retrieved from your separate Airtable waitlist table. This dashboard is only served on this laptop.</p><div class="bar"><span id="status" class="status">Loading entries…</span><a class="btn" href="/export.csv">Download CSV</a></div><div id="table"></div></div>
<script>
const statusNode=document.getElementById('status'),tableNode=document.getElementById('table');
function cell(value,label){const td=document.createElement('td');td.dataset.label=label;td.textContent=value||'—';return td;}
async function load(){try{const r=await fetch('/api/entries');const data=await r.json();if(!r.ok)throw new Error(data.error||'Could not load entries.');statusNode.textContent=`${data.length} ${data.length===1?'entry':'entries'} · refreshed ${new Date().toLocaleString()}`;if(!data.length){tableNode.innerHTML='<div class="empty">No waitlist entries yet.</div>';return;}const table=document.createElement('table'),head=document.createElement('thead'),hr=document.createElement('tr');['Name','Email','Brokerage','Team size','Joined','Status'].forEach(x=>{const th=document.createElement('th');th.textContent=x;hr.append(th)});head.append(hr);const body=document.createElement('tbody');for(const row of data){const tr=document.createElement('tr');tr.append(cell(row.name,'Name'),cell(row.email,'Email'),cell(row.brokerage,'Brokerage'),cell(row.teamSize,'Team size'),cell(row.joined,'Joined'),cell(row.status,'Status'));body.append(tr)}table.append(head,body);tableNode.replaceChildren(table);}catch(e){statusNode.textContent=e.message;statusNode.className='status error';}}
load();
</script></html>'''

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print('%s - %s' % (self.address_string(), fmt % args))

    def send_bytes(self, body, content_type, status=200, extra=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        if extra:
            for key, value in extra.items(): self.send_header(key, value)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def airtable_records(self):
        token = os.environ.get('AIRTABLE_TOKEN')
        base = os.environ.get('AIRTABLE_WAITLIST_BASE_ID')
        table = os.environ.get('AIRTABLE_WAITLIST_TABLE_ID')
        if not token or not base or not table:
            raise RuntimeError('Configure AIRTABLE_TOKEN, AIRTABLE_WAITLIST_BASE_ID, and AIRTABLE_WAITLIST_TABLE_ID in outputs/aether-waitlist/.env first.')
        from urllib.parse import quote
        url = f'https://api.airtable.com/v0/{quote(base, safe="")}/{quote(table, safe="")}'
        records, offset = [], None
        while True:
            params = {'pageSize': '100', 'sort[0][field]': 'Joined', 'sort[0][direction]': 'desc'}
            if offset: params['offset'] = offset
            req = Request(url + '?' + urlencode(params), headers={'Authorization': f'Bearer {token}'})
            with urlopen(req, timeout=20) as response:
                payload = json.load(response)
            for item in payload.get('records', []):
                fields = item.get('fields', {})
                records.append({
                    'name': fields.get('Name', ''), 'email': fields.get('Email', ''),
                    'brokerage': fields.get('Brokerage', ''), 'teamSize': fields.get('Team size', ''),
                    'joined': fields.get('Joined', ''), 'status': fields.get('Status', 'Waitlisted')
                })
            offset = payload.get('offset')
            if not offset: break
        return records

    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            return self.send_bytes(PAGE.encode(), 'text/html; charset=utf-8')
        if self.path == '/api/entries':
            try:
                data = json.dumps(self.airtable_records()).encode()
                return self.send_bytes(data, 'application/json; charset=utf-8')
            except (RuntimeError, HTTPError, URLError, TimeoutError) as exc:
                message = str(exc) if isinstance(exc, RuntimeError) else 'Could not connect to Airtable. Check your token, base, table, and internet connection.'
                return self.send_bytes(json.dumps({'error': message}).encode(), 'application/json; charset=utf-8', 503)
        if self.path == '/export.csv':
            try:
                output = io.StringIO(newline='')
                writer = csv.DictWriter(output, fieldnames=['name', 'email', 'brokerage', 'teamSize', 'joined', 'status'])
                writer.writeheader(); writer.writerows(self.airtable_records())
                return self.send_bytes(output.getvalue().encode('utf-8-sig'), 'text/csv; charset=utf-8', extra={'Content-Disposition': 'attachment; filename="aether-ai-waitlist.csv"'})
            except (RuntimeError, HTTPError, URLError, TimeoutError) as exc:
                message = str(exc) if isinstance(exc, RuntimeError) else 'Could not connect to Airtable. Check your token, base, table, and internet connection.'
                return self.send_bytes(message.encode(), 'text/plain; charset=utf-8', 503)
        return self.send_bytes(b'Not found', 'text/plain; charset=utf-8', 404)

if __name__ == '__main__':
    address = ('127.0.0.1', 8767)
    print(f'Waitlist dashboard: http://{address[0]}:{address[1]}')
    print('This dashboard binds to localhost only; keep .env private.')
    ThreadingHTTPServer(address, Handler).serve_forever()
