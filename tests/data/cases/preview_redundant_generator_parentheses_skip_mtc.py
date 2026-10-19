# flags: --preview --skip-magic-trailing-comma
# Removing the trailing comma leaves redundant parentheses around the generator.
consume((normalize(record) for record in records_loaded_from_the_database_for_today_and_yesterday),)

consume((
    normalize(record) for record in records_loaded_from_the_database_for_today_and_yesterday
))

# output
# Removing the trailing comma leaves redundant parentheses around the generator.
consume(
    normalize(record)
    for record in records_loaded_from_the_database_for_today_and_yesterday
)

consume(
    normalize(record)
    for record in records_loaded_from_the_database_for_today_and_yesterday
)
