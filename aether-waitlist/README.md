# Aether AI public waitlist + local dashboard

## What is included

- `index.html`: the landing page with a waitlist form.
- `api/waitlist.js`: a Vercel serverless endpoint that validates signups and saves them to Airtable.
- `dashboard.py`: a local-only dashboard that reads the Airtable waitlist and exports CSV.

The waitlist uses a separate Airtable table from borrower lead capture. Do not put borrower names, financial details, or loan information in this waitlist.

## Airtable setup

Create a new base called `Aether AI Waitlist` and a table called `Waitlist`. Add these fields with the exact names and types:

| Field | Airtable type |
|---|---|
| Name | Single line text |
| Email | Email |
| Brokerage | Single line text |
| Team size | Single line text |
| Status | Single line text |
| Joined | Date with time enabled |
| Consent | Checkbox |
| Source | Single line text |

Create a Personal Access Token limited to this waitlist base with record read/write access for Vercel. For the laptop dashboard, use a separate read-only token if possible.

## Vercel deployment

1. Add the contents of this folder to the Vercel project that will serve the landing page. The project root should contain `index.html` and `api/waitlist.js`.
2. In Vercel project settings, add `AIRTABLE_TOKEN`, `AIRTABLE_WAITLIST_BASE_ID`, and `AIRTABLE_WAITLIST_TABLE_ID` as environment variables. Use the write token and the new waitlist base/table IDs.
3. Deploy the project. The form posts to the same-origin `/api/waitlist` endpoint.
4. Before sharing the page, add the business's privacy-policy URL and confirm the terms for how long waitlist contact details are kept.

Never put an Airtable token in `index.html` or other browser code.

## Open the waitlist on this laptop

1. Copy `.env.example` to `.env` in this folder.
2. Put the Airtable values in `.env`. Use a read-only token for `AIRTABLE_TOKEN` here.
3. Start the dashboard from this folder with `python dashboard.py` (or the bundled Python runtime).
4. Open `http://127.0.0.1:8767` on this laptop. Select **Download CSV** to export the current list.

The dashboard is bound to `127.0.0.1` and is not exposed to the public internet. Entries remain in Airtable if this laptop is off. The `.env` file contains a secret and is excluded by `.gitignore`.

## Before it can accept public signups

The Vercel environment variables, separate Airtable table, and deployment must be configured. The workspace does not include an authenticated Vercel project or Airtable connection, so this folder is deployment-ready code rather than a live deployment.
