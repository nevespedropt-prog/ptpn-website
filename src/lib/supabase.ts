import { createClient } from '@supabase/supabase-js';

const url = import.meta.env.PUBLIC_SUPABASE_URL as string | undefined;
const key = import.meta.env.PUBLIC_SUPABASE_ANON_KEY as string | undefined;

function validUrl(v: string | undefined) {
  try { return Boolean(v && /^https?:$/.test(new URL(v).protocol)); } catch { return false; }
}

export const configured = validUrl(url) && Boolean(key);
export const supabase = createClient(
  configured ? url! : 'http://localhost',
  configured ? key! : 'missing',
);
