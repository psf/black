# flags: --preview
a = str(my_very_very_very_long_url_name.with_user(and_very_long_username).with_password(and_very_long_password))
a = my_very_very_very_long_url_name.with_user(and_very_long_username).with_password(and_very_long_password)


def foo():
    completion_time = (a.read_namespaced_job(job.metadata.name, namespace="default").status().completion_time())


# output

a = str(
    my_very_very_very_long_url_name.with_user(and_very_long_username)
    .with_password(and_very_long_password)
)
a = (
    my_very_very_very_long_url_name.with_user(and_very_long_username)
    .with_password(and_very_long_password)
)


def foo():
    completion_time = (
        a.read_namespaced_job(job.metadata.name, namespace="default")
        .status()
        .completion_time()
    )
