import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    '[Shop Command Center] VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY is not set. ' +
    'Copy frontend/.env.example to frontend/.env and fill in your Supabase credentials.'
  )
}

export const supabase = createClient(
  supabaseUrl  || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder-anon-key'
)
