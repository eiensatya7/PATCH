create table public.lob_applications
(
    lob_app_id            integer                                                 not null
        constraint lob_applications_pk
            primary key,
    application_name      varchar(100),
    lob                   varchar(10),
    auto_resolve          boolean     default true                                not null,
    environment           varchar(4)                                              not null,
    git_remote_url        varchar(255)                                            not null,
    lookup_branch_pattern varchar(50) default 'LATEST_RELEASE'::character varying not null,
    filter_pii            boolean     default false                               not null,
    created_ts            timestamp   default now()                               not null,
    updated_ts            timestamp   default now()                               not null,
    notification_dls      text                                                    not null
);

alter table public.lob_applications
    owner to patch_user;

create unique index lob_applications_lob_application_name_environment_uindex
    on public.lob_applications (lob, application_name, environment);

