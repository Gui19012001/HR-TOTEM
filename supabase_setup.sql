-- Perfil criado automaticamente quando alguém se cadastra no IBERO ATENDE.
create table if not exists public.rh_staff_profiles (
  email text primary key,
  auth_user_id uuid not null unique,
  display_name text not null,
  photo_url text,
  is_available boolean not null default false,
  approval_status text not null default 'pending' check (approval_status in ('pending','approved','rejected')),
  role text not null default 'attendant' check (role in ('admin','attendant')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.rh_staff_profiles enable row level security;

-- Fila temporária de solicitações do totem; sem gravação de mensagens/áudio/vídeo.
create table if not exists public.rh_rooms (
  id uuid primary key default gen_random_uuid(),
  nome text not null default 'Colaborador',
  tipo text not null check (tipo in ('Chat','Videochamada','Voz')),
  assunto text,
  descricao text,
  status text not null default 'pendente' check (status in ('pendente','em_atendimento','encerrado')),
  atendente text,
  room_token text,
  ficha_data jsonb,
  ficha_status text not null default 'nao_criada',
  ficha_accepted_at timestamptz,
  created_at timestamptz not null default now(),
  accepted_at timestamptz,
  expires_at timestamptz not null default (now() + interval '2 hours')
);
-- Migração segura para tabelas rh_rooms já existentes.
alter table public.rh_rooms add column if not exists room_token text;
alter table public.rh_rooms add column if not exists ficha_data jsonb;
alter table public.rh_rooms add column if not exists ficha_status text not null default 'nao_criada';
alter table public.rh_rooms add column if not exists ficha_accepted_at timestamptz;
create index if not exists rh_rooms_status_created_idx on public.rh_rooms(status, created_at);
alter table public.rh_rooms enable row level security;

-- O colaborador só pode confirmar a ficha da própria sala usando o token aleatório.
create or replace function public.rh_accept_ficha(p_room_id uuid, p_room_token text)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  changed_rows integer;
begin
  update public.rh_rooms
     set ficha_status = 'aceita', ficha_accepted_at = now()
   where id = p_room_id
     and room_token = p_room_token
     and status = 'em_atendimento'
     and ficha_status = 'aguardando_aceite';

  get diagnostics changed_rows = row_count;
  return changed_rows = 1;
end;
$$;
revoke all on function public.rh_accept_ficha(uuid, text) from public;
grant execute on function public.rh_accept_ficha(uuid, text) to anon, authenticated;

-- PROMOVER O PRIMEIRO ADMINISTRADOR:
-- 1. Cadastre a conta normalmente no app e confirme o e-mail.
-- 2. No SQL Editor, execute (substituindo pelo e-mail real):
-- update public.rh_staff_profiles
-- set role='admin', approval_status='approved'
-- where email='admin@empresa.com';
-- Depois disso, esse perfil aprova os demais pela tela do RH.

-- Crie no Supabase Storage um bucket público de leitura chamado rh-profiles.
-- O app acessa o banco e o Storage pelo backend, usando service role somente nos Secrets.
-- Limpe solicitações antigas periodicamente:
-- delete from public.rh_rooms where status='encerrado' or expires_at < now();
