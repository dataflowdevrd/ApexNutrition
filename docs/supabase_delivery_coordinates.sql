-- Ejecutar una vez en Supabase SQL Editor.
-- Guarda la ubicación seleccionada por el cliente para evitar geocodificar
-- direcciones ambiguas en el país equivocado.

alter table public.deliveries
    add column if not exists destino_lat double precision,
    add column if not exists destino_lng double precision;

do $$
begin
    if not exists (
        select 1 from pg_constraint where conname = 'deliveries_destino_lat_check'
    ) then
        alter table public.deliveries add constraint deliveries_destino_lat_check
            check (destino_lat is null or (destino_lat between -90 and 90));
    end if;
    if not exists (
        select 1 from pg_constraint where conname = 'deliveries_destino_lng_check'
    ) then
        alter table public.deliveries add constraint deliveries_destino_lng_check
            check (destino_lng is null or (destino_lng between -180 and 180));
    end if;
end $$;