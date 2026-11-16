-- Report Generator · Lectura autorizada del corpus para los usuarios de la aplicación
-- Ejecutar una vez en el SQL Editor, después de 01_historial.sql.
--
-- Problema: el SQL de la Clase 08 protege clase08_fragmentos con owner_id = auth.uid(),
-- así que solo la cuenta que cargó el corpus puede leerlo. Los demás usuarios de la app
-- no recuperarían evidencia.
--
-- Solución (sin desactivar RLS ni usar una clave administrativa):
--   1. app_lectores_corpus: lista explícita de usuarios que el propietario autoriza a LEER su corpus.
--   2. Una política SELECT adicional sobre clase08_fragmentos para esos lectores. No da INSERT/UPDATE/DELETE.
--   3. app_buscar_fragmentos: búsqueda vectorial SECURITY INVOKER (respeta RLS del que pregunta).
--
-- El historial sigue siendo privado: estas reglas no tocan conversaciones ni mensajes.

create table if not exists public.app_lectores_corpus (
    corpus_id       text not null,
    propietario_id  uuid not null default auth.uid() references auth.users (id) on delete cascade,
    lector_id       uuid not null references auth.users (id) on delete cascade,
    agregado_en     timestamptz not null default now(),
    primary key (corpus_id, propietario_id, lector_id)
);

revoke all on public.app_lectores_corpus from anon;
grant select, insert, delete on public.app_lectores_corpus to authenticated;
alter table public.app_lectores_corpus enable row level security;

-- El propietario administra a quién autoriza; cada lector solo ve su propia autorización.
drop policy if exists lectores_select on public.app_lectores_corpus;
create policy lectores_select on public.app_lectores_corpus
    for select to authenticated
    using (propietario_id = (select auth.uid()) or lector_id = (select auth.uid()));

drop policy if exists lectores_insert_propietario on public.app_lectores_corpus;
create policy lectores_insert_propietario on public.app_lectores_corpus
    for insert to authenticated
    with check (propietario_id = (select auth.uid()));

drop policy if exists lectores_delete_propietario on public.app_lectores_corpus;
create policy lectores_delete_propietario on public.app_lectores_corpus
    for delete to authenticated
    using (propietario_id = (select auth.uid()));

-- Política adicional (permisiva) de solo lectura sobre el corpus de la Clase 08.
drop policy if exists fragmentos_lectura_autorizada on public.clase08_fragmentos;
create policy fragmentos_lectura_autorizada on public.clase08_fragmentos
    for select to authenticated
    using (exists (select 1 from public.app_lectores_corpus l
                   where l.corpus_id = clase08_fragmentos.corpus_id
                     and l.propietario_id = clase08_fragmentos.owner_id
                     and l.lector_id = (select auth.uid())));

-- Búsqueda vectorial. Supone la columna `embedding vector(384)` de la Clase 08.
-- Si en vuestro esquema la columna tiene otro nombre, cambiadlo en las dos líneas marcadas.
create or replace function public.app_buscar_fragmentos(
    query_embedding vector(384),
    p_owner_id      uuid,
    p_corpus_id     text,
    p_modelo        text,
    p_revision      text,
    match_count     int default 10
)
returns table (chunk_id text, content text, metadata jsonb, similitud double precision)
language sql
stable
security invoker
set search_path = public, extensions
as $$
    select f.chunk_id::text, f.content, f.metadata,
           1 - (f.embedding <=> query_embedding) as similitud          -- columna embedding
    from public.clase08_fragmentos f
    where f.owner_id = p_owner_id
      and f.corpus_id = p_corpus_id
      and f.configuracion ->> 'modelo' = p_modelo
      and f.configuracion ->> 'revision' = p_revision
    order by f.embedding <=> query_embedding, f.chunk_id               -- columna embedding
    limit least(greatest(match_count, 1), 50);
$$;

revoke execute on function public.app_buscar_fragmentos(vector, uuid, text, text, text, int) from public, anon;
grant execute on function public.app_buscar_fragmentos(vector, uuid, text, text, text, int) to authenticated;

-- ---------------------------------------------------------------------------
-- Autorizar lectores. Desde el SQL Editor (que no tiene auth.uid()) indicamos
-- el propietario de forma explícita. Sustituid los correos por los reales.
--
-- insert into public.app_lectores_corpus (corpus_id, propietario_id, lector_id)
-- select 'report_generator-ff98b1398c56', p.id, l.id
-- from auth.users p, auth.users l
-- where p.email = 'PROPIETARIO_DEL_CORPUS@ejemplo.com'
--   and l.email in ('usuario1@ejemplo.com', 'usuario2@ejemplo.com')
-- on conflict do nothing;
--
-- UUID del propietario para CORPUS_PROPIETARIO_ID:
-- select id from auth.users where email = 'PROPIETARIO_DEL_CORPUS@ejemplo.com';
