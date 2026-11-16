-- Report Generator · Historial de conversaciones por usuario
-- Ejecutar una vez en el SQL Editor del mismo proyecto de Supabase que contiene el corpus.
-- Es idempotente: se puede volver a ejecutar sin perder datos.
--
-- Diseño:
--   conversaciones: una fila por conversación, con su propietario (auth.users).
--   mensajes:       preguntas y respuestas en orden estable (id identity), ligadas a una conversación.
--   No hay política DELETE: crear una conversación nueva nunca borra las anteriores.

create table if not exists public.conversaciones (
    id              uuid primary key default gen_random_uuid(),
    usuario_id      uuid not null default auth.uid() references auth.users (id) on delete cascade,
    titulo          text not null default 'Nueva conversación'
                    check (char_length(titulo) between 1 and 120),
    creada_en       timestamptz not null default now(),
    actualizada_en  timestamptz not null default now()
);
create index if not exists conversaciones_usuario_idx
    on public.conversaciones (usuario_id, actualizada_en desc);

create table if not exists public.mensajes (
    id               bigint generated always as identity primary key,
    conversacion_id  uuid not null references public.conversaciones (id) on delete cascade,
    usuario_id       uuid not null default auth.uid() references auth.users (id) on delete cascade,
    rol              text not null check (rol in ('user', 'assistant')),
    contenido        text not null check (char_length(contenido) between 1 and 20000),
    estado           text,                                   -- RESPONDER, ACLARAR, RECHAZAR, ERROR_TECNICO...
    fuentes          jsonb not null default '{}'::jsonb,     -- etiquetas F/T citadas y su procedencia
    traza            jsonb not null default '{}'::jsonb,     -- eventos, operaciones, duración (sin secretos)
    creado_en        timestamptz not null default now()
);
create index if not exists mensajes_conversacion_idx on public.mensajes (conversacion_id, id);

-- Permisos de tabla: el rol anónimo no ve nada; el autenticado solo lo que RLS permita.
revoke all on public.conversaciones from anon;
revoke all on public.mensajes from anon;
grant select, insert on public.conversaciones to authenticated;
grant update (titulo, actualizada_en) on public.conversaciones to authenticated;
grant select, insert on public.mensajes to authenticated;

alter table public.conversaciones enable row level security;
alter table public.mensajes enable row level security;

-- Conversaciones: solo su propietario las lee, crea o renombra.
drop policy if exists conversaciones_select_propias on public.conversaciones;
create policy conversaciones_select_propias on public.conversaciones
    for select to authenticated
    using (usuario_id = (select auth.uid()));

drop policy if exists conversaciones_insert_propias on public.conversaciones;
create policy conversaciones_insert_propias on public.conversaciones
    for insert to authenticated
    with check (usuario_id = (select auth.uid()));

drop policy if exists conversaciones_update_propias on public.conversaciones;
create policy conversaciones_update_propias on public.conversaciones
    for update to authenticated
    using (usuario_id = (select auth.uid()))
    with check (usuario_id = (select auth.uid()));

-- Mensajes: se leen o insertan solo si la conversación pertenece a quien pregunta.
-- Conocer el UUID de una conversación ajena no concede acceso.
drop policy if exists mensajes_select_propios on public.mensajes;
create policy mensajes_select_propios on public.mensajes
    for select to authenticated
    using (exists (select 1 from public.conversaciones c
                   where c.id = mensajes.conversacion_id
                     and c.usuario_id = (select auth.uid())));

drop policy if exists mensajes_insert_propios on public.mensajes;
create policy mensajes_insert_propios on public.mensajes
    for insert to authenticated
    with check (usuario_id = (select auth.uid())
                and exists (select 1 from public.conversaciones c
                            where c.id = mensajes.conversacion_id
                              and c.usuario_id = (select auth.uid())));
