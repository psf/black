# flags: --preview
asm_client: SecretsManagerClient = boto3.client("secretsmanager")  # pyright: ignore[reportUnknownMemberType]
long_call = some_function(argument_one, argument_two)  # pyright: ignore[reportUnknownVariableType]
short = foo("x")  # ty: ignore[call-overload]
unchanged = foo("x")  # type: ignore[call-overload]
type_ignore_long = some_module.compute(argument_one, argument_two, argument_three)  # type: ignore
already_split = (
    foo("x")  # pyright: ignore[call-overload]
)
no_pragma = some_function(argument_one, argument_two, argument_three, argument_four, argument_five)
prose_long = some_function(argument_one, argument_two, argument_three)  # this is not a pragma

# output

asm_client: SecretsManagerClient = boto3.client("secretsmanager")  # pyright: ignore[reportUnknownMemberType]
long_call = some_function(argument_one, argument_two)  # pyright: ignore[reportUnknownVariableType]
short = foo("x")  # ty: ignore[call-overload]
unchanged = foo("x")  # type: ignore[call-overload]
type_ignore_long = some_module.compute(argument_one, argument_two, argument_three)  # type: ignore
already_split = foo("x")  # pyright: ignore[call-overload]
no_pragma = some_function(
    argument_one, argument_two, argument_three, argument_four, argument_five
)
prose_long = some_function(
    argument_one, argument_two, argument_three
)  # this is not a pragma
