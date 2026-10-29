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
4. The signup form links to `privacy.html` and uses the retention terms shown there. Review the policy against your actual practices before sharing the page.

Never put an Airtable token in `index.html` or other browser code.

## Open the waitlist on this laptop

1. Copy `.env.example` to `.env` in this folder.
2. Put the Airtable values in `.env`. Use a read-only token for `AIRTABLE_TOKEN` here.
3. Start the dashboard from this folder with `python dashboard.py` (or the bundled Python runtime).
4. Open `http://127.0.0.1:8767` on this laptop. Select **Download CSV** to export the current list.

The dashboard is bound to `127.0.0.1` and is not exposed to the public internet. Entries remain in Airtable if this laptop is off. The `.env` file contains a secret and is excluded by `.gitignore`.

## Before it can accept public signups

The Vercel environment variables, separate Airtable table, and deployment must be configured. The workspace contains the page and function source, but it is not yet linked to a Vercel project. Add this folder to the correct project and deploy after the environment variables are configured.

## Privacy and launch checks

- The public policy is `privacy.html`; review that it matches the live form, hosting, storage, and contact practices before deployment.
- The policy now uses the retention rule selected for AETHER AI: keep entries while the waitlist is active, review the active status at least annually, and delete or anonymize entries within 90 days after closing it (subject to the stated exceptions). Set a calendar reminder and follow this schedule in Airtable.
- AETHER AI operates from Nigeria and the waitlist is intended for U.S. brokers. Before live submissions, identify and document the applicable lawful transfer basis and safeguards for each international transfer under Nigeria's Data Protection Act, including the Airtable and Vercel account terms. Do not assume a provider's DPA is executed or applicable; confirm this from the actual account and plan.
- Confirm whether “AETHER AI” is the controller's legal identity or only a trade name. If there is a registered owner/entity name, update the privacy notice to name it alongside the brand.
- Keep the waitlist limited to broker contact details. Any future borrower-data processing needs separate product privacy terms, documented workflows, and a review of applicable financial/privacy obligations.
- The policy is a working notice, not a legal opinion or a certification of compliance. Have counsel or a Nigeria data-protection professional review it before public launch, particularly the cross-border transfer basis and any Texas-law applicability.

