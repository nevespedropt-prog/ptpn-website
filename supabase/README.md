# PTPN Website — Supabase setup (one-time)

Project: dstxexfkxejmolnulwli (same DB as the PTPN app)

## 1) Run the migration
Supabase Dashboard → SQL Editor → New query → paste the entire file:
  supabase/migrations/20261028_website_backend.sql
→ Run. Creates: enquiries, client_packages, payments, client_balances view, notify trigger.

## 2) Deploy the edge function
From any machine with Supabase CLI logged in:
  supabase link --project-ref dstxexfkxejmolnulwli
  supabase functions deploy send-enquiry-email --no-verify-jwt
Or via Dashboard → Edge Functions → New → paste supabase/functions/send-enquiry-email/index.ts

## 3) Set secrets (Dashboard → Edge Functions → Secrets, or CLI)
Required:
  RESEND_API_KEY        — from resend.com (free tier is fine), leave unset and emails are just logged
Optional (defaults shown):
  ENQUIRY_NOTIFY_TO     — info@ptpn.co.uk
  ENQUIRY_NOTIFY_FROM   — PTPN <noreply@ptpn.co.uk>

## 4) Website env
Copy .env.example → .env and fill PUBLIC_SUPABASE_ANON_KEY (the publishable key already in this repo's .env is correct).
Build is static — no server. Enquiry form inserts directly via Supabase JS + RLS.

## 5) Verify
- Visit /admin → sign in as coach → Enquiries should load (empty is fine).
- Submit the enquiry form on / → row appears in Enquiries, email sent if Resend is configured.
- Packages/Payments/Sessions tabs are coach-only (is_coach() check).
