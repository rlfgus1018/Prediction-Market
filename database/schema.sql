create table if not exists news_raw (
  id bigserial primary key,
  source text not null,
  publisher text,
  title text not null,
  summary text,
  url text unique not null,
  url_hash text,
  published_at timestamptz,
  collected_at timestamptz not null,
  raw_payload jsonb not null
);

create table if not exists news_clean (
  news_id bigint primary key references news_raw(id) on delete cascade,
  clean_title text not null,
  clean_body text,
  language text not null default 'ko',
  duplicate_group_id text,
  is_duplicate boolean not null default false
);

create table if not exists news_features (
  news_id bigint primary key references news_raw(id) on delete cascade,
  sentiment_label text,
  sentiment_score numeric,
  event_type text,
  importance_score numeric,
  novelty_score numeric,
  market_relevance_score numeric,
  entities jsonb,
  sectors jsonb,
  created_at timestamptz not null default now()
);

create table if not exists index_bars (
  symbol text not null,
  date date not null,
  open numeric,
  high numeric,
  low numeric,
  close numeric not null,
  volume numeric,
  primary key(symbol, date)
);

create table if not exists daily_features (
  target_date date not null,
  symbol text not null,
  feature_json jsonb not null,
  label_up int,
  forward_return numeric,
  primary key(target_date, symbol)
);

create table if not exists predictions (
  id bigserial primary key,
  prediction_date date not null,
  target_symbol text not null,
  horizon text not null,
  model_version text not null,
  prob_up numeric not null,
  expected_return numeric,
  confidence numeric,
  explanation jsonb,
  created_at timestamptz not null default now(),
  unique(prediction_date, target_symbol, horizon, model_version)
);
