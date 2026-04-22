-- Shop Command Center — User Profiles Migration
-- Creates the shop_profiles table, enables RLS, and auto-creates
-- a profile row when a new user signs up via Supabase Auth.

-- 1. Shop profiles table
create table if not exists public.shop_profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  shop_name     text,
  owner_name    text,
  phone         text,
  address       text,
  location      text,
  hours         text,
  services      text[],
  business_type text default 'Auto Repair',
  website       text,
  tagline       text,
  tone          text default 'Professional and friendly',
  review_links  jsonb default '{}',
  social_media  jsonb default '{}',
  setup_complete boolean default false,
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

-- 2. Enable Row Level Security
alter table public.shop_profiles enable row level security;

-- 3. RLS Policies — owners can only see and edit their own row
create policy "Owner can view own profile"
  on public.shop_profiles for select
  using (auth.uid() = id);

create policy "Owner can insert own profile"
  on public.shop_profiles for insert
  with check (auth.uid() = id);

create policy "Owner can update own profile"
  on public.shop_profiles for update
  using (auth.uid() = id);

-- 4. Auto-create a profile row on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public
as $$
begin
  insert into public.shop_profiles (id)
  values (new.id)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- 5. Updated-at helper
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger shop_profiles_updated_at
  before update on public.shop_profiles
  for each row execute procedure public.set_updated_at();
