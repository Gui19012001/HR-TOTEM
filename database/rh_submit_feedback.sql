-- Executar uma vez no Supabase SQL Editor do projeto IBERO ATENDE.
-- A função valida o token da sala e grava a avaliação junto da ficha temporária.
create or replace function public.rh_submit_feedback(
    p_room_id text,
    p_room_token text,
    p_satisfaction integer,
    p_resolved text
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
begin
    if p_satisfaction is null or p_satisfaction not between 1 and 5 then
        raise exception 'Nota de satisfação inválida.';
    end if;
    if p_resolved is null or p_resolved not in ('Sim', 'Parcialmente', 'Não') then
        raise exception 'Resposta de solução inválida.';
    end if;

    update public.rh_rooms
       set ficha_data = coalesce(ficha_data::jsonb, '{}'::jsonb) || jsonb_build_object(
               'avaliacao_satisfacao', p_satisfaction,
               'avaliacao_solucionado', p_resolved,
               'avaliacao_enviada_em', now()
           ),
           status = 'encerrado',
           ficha_status = 'concluida'
     where id::text = p_room_id
       and room_token = p_room_token
       and status = 'aguardando_avaliacao'
       and ficha_status = 'aguardando_avaliacao';

    return found;
end;
$$;

revoke all on function public.rh_submit_feedback(text, text, integer, text) from public;
grant execute on function public.rh_submit_feedback(text, text, integer, text) to anon, authenticated;
