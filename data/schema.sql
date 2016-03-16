drop table if exists profile;

create table profile (
    id integer primary key autoincrement,
    identity_id text not null,
    name text not null,
    email text not null,
    project text
);
