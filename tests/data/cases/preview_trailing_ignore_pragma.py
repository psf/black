# flags: --preview
asm_client: SecretsManagerClient = boto3.client("secretsmanager")  # pyright: ignore[reportUnknownMemberType]
long_call = some_function(argument_one, argument_two)  # pyright: ignore[reportUnknownVariableType]
short = foo("x")  # ty: ignore[call-overload]
unchanged = foo("x")  # type: ignore[call-overload]
already_split = (
    foo("x")  # pyright: ignore[call-overload]
)
no_pragma = some_function(argument_one, argument_two, argument_three, argument_four)

# output

asm_client: SecretsManagerClient = boto3.client(  # pyright: ignore[reportUnknownMemberType]
    "secretsmanager"
)
long_call = some_function(  # pyright: ignore[reportUnknownVariableType]
    argument_one, argument_two
)
short = foo("x")  # ty: ignore[call-overload]
unchanged = foo("x")  # type: ignore[call-overload]
already_split = foo("x")  # pyright: ignore[call-overload]
no_pragma = some_function(argument_one, argument_two, argument_three, argument_four)
