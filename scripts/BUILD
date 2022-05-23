python_sources()

python_requirements(
    name="scripts_requirements",
    source="scripts_requirements.txt",
    resolve="scripts",
)

python_requirements(
    name="diff_shades_requirements",
    source="diff_shades_requirements.txt",
    resolve="diff_shades",
)

pex_binary(
    name="check_pre_commit_rev_in_example",
    entry_point="check_pre_commit_rev_in_example.py",
    resolve="scripts",
)

pex_binary(
    name="check_version_in_basics_example",
    entry_point="check_version_in_basics_example.py",
    resolve="scripts",
)

pex_binary(
    name="diff_shades_gha_helper",
    entry_point="diff_shades_gha_helper.py",
    resolve="diff_shades",
)
