create table images (
  image_id serial primary key,
  filename varchar(255),
  tags text[] not null default '{}'
);
