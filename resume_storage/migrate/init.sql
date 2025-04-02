
create table Resume (
    resume_id serial primary key,
    user_id int not null,
    created_at timestamp default now(),
    title varchar(1024) not null
);

create index idx_resume_user_id on Resume (user_id);

