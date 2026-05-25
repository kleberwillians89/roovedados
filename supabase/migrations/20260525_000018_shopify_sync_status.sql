create table if not exists public.shopify_sync_status (
  client_id text not null,
  shop_domain text not null default '',
  last_sync_at timestamptz not null default now(),
  last_sync_status text not null default 'success',
  orders_found integer not null default 0,
  orders_persisted integer not null default 0,
  items_persisted integer not null default 0,
  customers_persisted integer not null default 0,
  refunds_persisted integer not null default 0,
  pages integer not null default 0,
  updated_at timestamptz not null default now(),
  primary key (client_id, shop_domain)
);

create index if not exists idx_shopify_sync_status_client_last_sync
  on public.shopify_sync_status(client_id, last_sync_at desc);
