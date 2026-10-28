-- PTPN website backend — run once in Supabase SQL Editor
-- Uses existing project dstxexfkxejmolnulwli (same DB as the app).
-- 3 tables: enquiries (public form), client_packages, payments (manual ledger).
-- Emails are sent by the edge function supabase/functions/send-enquiry-email
-- triggered below via pg_net (no cron, no cost).

-- ========== 1. Enquiries ==========
create table if not exists public.enquiries (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 2 and 120),
  email text not null check (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  phone text not null default '',
  package text not null default 'Not sure yet, advise me',
  goal text not null default '',
  frequency text not null default '',
  message text not null default '',
  status text not null default 'new' check (status in ('new','contacted','converted','lost','spam')),
  created_at timestamptz not null default now()
);
create index if not exists enquiries_created on public.enquiries (created_at desc);
create index if not exists enquiries_status on public.enquiries (status);
alter table public.enquiries enable row level security;
drop policy if exists "enquiries insert anyone" on public.enquiries;
create policy "enquiries insert anyone" on public.enquiries for insert with check (true);
drop policy if exists "enquiries read coach" on public.enquiries;
create policy "enquiries read coach" on public.enquiries for select using (public.is_coach());
drop policy if exists "enquiries update coach" on public.enquiries;
create policy "enquiries update coach" on public.enquiries for update using (public.is_coach()) with check (public.is_coach());
drop policy if exists "enquiries delete coach" on public.enquiries;
create policy "enquiries delete coach" on public.enquiries for delete using (public.is_coach());

-- ========== 2. Client packages (which pack a client bought) ==========
create table if not exists public.client_packages (
  id uuid primary key default gen_random_uuid(),
  client_id uuid not null references public.profiles(id) on delete cascade,
  package_name text not null check (package_name in ('Express','Ignition','Momentum','Signature','Duo')),
  sessions_total int not null check (sessions_total > 0),
  sessions_used int not null default 0 check (sessions_used >= 0),
  total_gbp numeric(10,2) not null check (total_gbp >= 0),
  status text not null default 'active' check (status in ('active','completed','cancelled')),
  started_on date not null default current_date,
  notes text not null default '',
  created_at timestamptz not null default now(),
  constraint sessions_used_lte_total check (sessions_used <= sessions_total)
);
create index if not exists client_packages_client on public.client_packages (client_id);
alter table public.client_packages enable row level security;
drop policy if exists "packages read own or coach" on public.client_packages;
create policy "packages read own or coach" on public.client_packages for select using (client_id = auth.uid() or public.is_coach());
drop policy if exists "packages coach write" on public.client_packages;
create policy "packages coach write" on public.client_packages for all using (public.is_coach()) with check (public.is_coach());

-- ========== 3. Payments ledger (you enter amounts — no Stripe) ==========
create table if not exists public.payments (
  id uuid primary key default gen_random_uuid(),
  client_id uuid not null references public.profiles(id) on delete cascade,
  package_id uuid references public.client_packages(id) on delete set null,
  amount_gbp numeric(10,2) not null check (amount_gbp <> 0),
  method text not null default 'cash' check (method in ('cash','bank','other')),
  paid_on date not null default current_date,
  note text not null default '',
  created_by uuid references public.profiles(id),
  created_at timestamptz not null default now()
);
create index if not exists payments_client on public.payments (client_id, paid_on desc);
alter table public.payments enable row level security;
drop policy if exists "payments read own or coach" on public.payments;
create policy "payments read own or coach" on public.payments for select using (client_id = auth.uid() or public.is_coach());
drop policy if exists "payments coach write" on public.payments;
create policy "payments coach write" on public.payments for all using (public.is_coach()) with check (public.is_coach());

-- ========== 4. Balance view (what's owed vs paid) ==========
create or replace view public.client_balances as
select
  p.id as client_id,
  coalesce(pkg.owed, 0) as owed_gbp,
  coalesce(pay.paid, 0) as paid_gbp,
  coalesce(pkg.owed, 0) - coalesce(pay.paid, 0) as balance_gbp
from public.profiles p
left join (select client_id, sum(total_gbp) as owed from public.client_packages where status <> 'cancelled' group by client_id) pkg on pkg.client_id = p.id
left join (select client_id, sum(amount_gbp) as paid from public.payments group by client_id) pay on pay.client_id = p.id
where p.role = 'client';

-- ========== 5. Email trigger for new enquiries ==========
-- Calls the edge function via pg_net (already enabled for send-push). If pg_net is not
-- available the insert still succeeds — the function just won't be called automatically
-- and you can call it manually from the admin "Resend email" button.
create or replace function public.notify_new_enquiry()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  supa_url text := 'https://dstxexfkxejmolnulwli.supabase.co';
  -- pg_net is the same extension the app's send-push uses; skip silently if absent
begin
  begin
    perform net.http_post(
      url := supa_url || '/functions/v1/send-enquiry-email',
      headers := jsonb_build_object('Content-Type','application/json'),
      body := jsonb_build_object('enquiry_id', new.id)
    );
  exception when undefined_function then null;
              when others then null;
  end;
  return new;
end $$;

drop trigger if exists trg_notify_new_enquiry on public.enquiries;
create trigger trg_notify_new_enquiry after insert on public.enquiries
for each row execute function public.notify_new_enquiry();

-- Keep helper locked down
revoke execute on function public.notify_new_enquiry() from public, anon, authenticated;
