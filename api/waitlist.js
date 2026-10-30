module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed.' });
  }
  const origin = req.headers.origin;
  const host = req.headers.host;
  if (origin && host && new URL(origin).host !== host) {
    return res.status(403).json({ error: 'Request origin not allowed.' });
  }
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  if (body.website) return res.status(200).json({ ok: true });
  const clean = (value, max) => typeof value === 'string' ? value.trim().replace(/[<>]/g, '').slice(0, max) : '';
  const name = clean(body.name, 100);
  const email = clean(body.email, 254).toLowerCase();
  const brokerage = clean(body.brokerage, 120);
  const teamSize = clean(body.teamSize, 40);
  if (!name || !brokerage || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || body.consent !== true) {
    return res.status(400).json({ error: 'Enter your name, valid work email, brokerage, and consent to continue.' });
  }
  const { AIRTABLE_TOKEN, AIRTABLE_WAITLIST_BASE_ID, AIRTABLE_WAITLIST_TABLE_ID } = process.env;
  if (!AIRTABLE_TOKEN || !AIRTABLE_WAITLIST_BASE_ID || !AIRTABLE_WAITLIST_TABLE_ID) {
    return res.status(503).json({ error: 'The waitlist is not connected yet.' });
  }
  const endpoint = `https://api.airtable.com/v0/${encodeURIComponent(AIRTABLE_WAITLIST_BASE_ID)}/${encodeURIComponent(AIRTABLE_WAITLIST_TABLE_ID)}`;
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { Authorization: `Bearer ${AIRTABLE_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ records: [{ fields: {
        Name: name, Email: email, Brokerage: brokerage, 'Team size': teamSize,
        Status: 'Waitlisted', Joined: new Date().toISOString(), Consent: true, Source: 'Aether AI landing page'
      } }] })
    });
    if (!response.ok) {
      console.error('Airtable waitlist write failed:', response.status);
      return res.status(502).json({ error: 'We could not save your details right now. Please try again.' });
    }
    return res.status(201).json({ ok: true });
  } catch (error) {
    console.error('Waitlist storage request failed.');
    return res.status(502).json({ error: 'We could not save your details right now. Please try again.' });
  }
};
