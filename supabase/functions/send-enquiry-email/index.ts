import { createClient } from 'npm:@supabase/supabase-js@2'

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}
const json = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { ...cors, 'Content-Type': 'application/json' } })

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors })
  // Triggered by DB (pg_net) or manually from admin — no auth check, id is enough
  const body = await req.json().catch(() => ({})) as { enquiry_id?: string }

  const supaUrl = Deno.env.get('SUPABASE_URL')!
  const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  const resendKey = Deno.env.get('RESEND_API_KEY') ?? ''
  const notifyTo = Deno.env.get('ENQUIRY_NOTIFY_TO') ?? 'info@ptpn.co.uk'
  const notifyFrom = Deno.env.get('ENQUIRY_NOTIFY_FROM') ?? 'PTPN <noreply@ptpn.co.uk>'

  const db = createClient(supaUrl, serviceKey)

  let enquiry: Record<string, string> | null = null
  if (body.enquiry_id) {
    const { data } = await db.from('enquiries').select('*').eq('id', body.enquiry_id).maybeSingle()
    enquiry = data as Record<string, string> | null
  }
  // If called without id (manual test), skip DB lookup — still return ok
  if (!enquiry && !body.enquiry_id) return json({ ok: true, note: 'no enquiry_id, nothing to send' })
  if (!enquiry) return json({ error: 'enquiry not found' }, 404)

  const subject = `New enquiry — ${enquiry.name} · ${enquiry.package || 'PTPN'}`
  const text =
    `New enquiry from ${enquiry.name} <${enquiry.email}>\n` +
    `Phone: ${enquiry.phone || '—'}\n` +
    `Package: ${enquiry.package}\n` +
    `Goal: ${enquiry.goal || '—'} · Frequency: ${enquiry.frequency || '—'}\n\n` +
    `Message:\n${enquiry.message || '—'}\n\n` +
    `— PTPN website`

  const autoReplySubject = 'Thanks for getting in touch — PTPN'
  const autoReplyText =
    `Hi ${enquiry.name.split(' ')[0]},\n\n` +
    `Thanks for your enquiry. Pedro will come back to you personally, usually within one working day.\n\n` +
    `If anything changes in the meantime, just reply to this email.\n\n` +
    `Pedro — PTPN · Be fit\nBush Hill Park, Enfield\n`

  if (!resendKey) {
    console.log('[send-enquiry-email] RESEND_API_KEY not set — would have sent:', { subject, to: notifyTo, enquiry_id: enquiry.id })
    return json({ ok: true, emailed: false, reason: 'RESEND_API_KEY not set (logged only)' })
  }

  async function send(to: string, subj: string, txt: string) {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: notifyFrom, to, subject: subj, text: txt }),
    })
    const j = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(`Resend ${r.status}: ${JSON.stringify(j)}`)
    return j
  }

  try {
    await send(notifyTo, subject, text)
    // Auto-reply is best-effort — don't fail the whole call if the enquirer's address bounces
    try { await send(enquiry.email, autoReplySubject, autoReplyText) } catch (e) { console.warn('auto-reply failed', e) }
    return json({ ok: true, emailed: true })
  } catch (e) {
    console.error(e)
    return json({ error: String(e) }, 500)
  }
})
