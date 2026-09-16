-- Ejecutar en Supabase SQL Editor.
-- La funcion reemplaza el trigger de descuento para que la venta sea atomica.

drop policy if exists "anon_actualizar_productos" on public.productos;
create policy "anon_actualizar_productos"
on public.productos for update to anon
using (true) with check (true);

drop policy if exists "anon_eliminar_productos" on public.productos;
create policy "anon_eliminar_productos"
on public.productos for delete to anon
using (true);

drop policy if exists "anon_actualizar_lotes" on public.lotes;
create policy "anon_actualizar_lotes"
on public.lotes for update to anon
using (true) with check (true);

drop policy if exists "anon_eliminar_lotes" on public.lotes;
create policy "anon_eliminar_lotes"
on public.lotes for delete to anon
using (true);

drop policy if exists "anon_insertar_deliveries" on public.deliveries;
create policy "anon_insertar_deliveries"
on public.deliveries for insert to anon
with check (true);

drop policy if exists "anon_leer_deliveries" on public.deliveries;
create policy "anon_leer_deliveries"
on public.deliveries for select to anon
using (true);

drop policy if exists "anon_actualizar_deliveries" on public.deliveries;
create policy "anon_actualizar_deliveries"
on public.deliveries for update to anon
using (true) with check (true);

drop trigger if exists trg_descontar_stock on public.detalle_ventas;

drop function if exists public.registrar_venta_transaccional(
    uuid, text, text, text, text, numeric, numeric, numeric, jsonb
);

create or replace function public.registrar_venta_transaccional(
    p_cliente_id uuid,
    p_codigo_factura text,
    p_tipo_ncf text,
    p_ncf text,
    p_metodo_pago text,
    p_subtotal numeric,
    p_itbis numeric,
    p_total numeric,
    p_items jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    venta_id uuid;
    creado_en timestamptz;
    item jsonb;
    stock_actual integer;
    item_lote_id uuid;
    item_cantidad integer;
begin
    insert into public.ventas (
        cliente_id,
        codigo_factura,
        tipo_ncf,
        ncf,
        metodo_pago,
        subtotal_dop,
        itbis_dop,
        monto_total_dop,
        estado_factura
    ) values (
        p_cliente_id,
        p_codigo_factura,
        p_tipo_ncf,
        p_ncf,
        p_metodo_pago,
        p_subtotal,
        p_itbis,
        p_total,
        'EMITIDA'
    )
    returning id, public.ventas.creado_en into venta_id, creado_en;

    for item in select value from jsonb_array_elements(p_items)
    loop
        item_lote_id := (item->>'lote_id')::uuid;
        item_cantidad := (item->>'cantidad')::integer;

        select cantidad_actual
        into stock_actual
        from public.lotes
        where id = item_lote_id
        for update;

        if stock_actual is null then
            raise exception 'Lote no encontrado: %', item_lote_id;
        end if;

        if stock_actual < item_cantidad then
            raise exception 'Stock insuficiente para el lote %', item_lote_id;
        end if;

        insert into public.detalle_ventas (
            venta_id,
            lote_id,
            cantidad,
            precio_unitario_dop,
            subtotal_linea_dop
        ) values (
            venta_id,
            item_lote_id,
            item_cantidad,
            (item->>'precio_unitario')::numeric,
            round(item_cantidad * (item->>'precio_unitario')::numeric, 2)
        );

        update public.lotes
        set cantidad_actual = cantidad_actual - item_cantidad,
            estado = case
                when cantidad_actual - item_cantidad = 0 then 'AGOTADO'
                else estado
            end
        where id = item_lote_id;
    end loop;

    return jsonb_build_object(
        'id', venta_id,
        'codigo_factura', p_codigo_factura,
        'ncf', p_ncf,
        'subtotal', p_subtotal,
        'itbis', p_itbis,
        'total', p_total,
        'estado', 'EMITIDA',
        'creado_en', creado_en
    );
end;
$$;

grant execute on function public.registrar_venta_transaccional(
    uuid, text, text, text, text, numeric, numeric, numeric, jsonb
) to anon, authenticated;
