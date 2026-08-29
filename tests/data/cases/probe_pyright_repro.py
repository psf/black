asm_client: SecretsManagerClient = boto3.client("secretsmanager")  # pyright: ignore[reportUnknownMemberType]
asm_client: SecretsManagerClient = boto3.client(  # pyright: ignore[reportUnknownMemberType]
    "secretsmanager"
)
asm_client: SecretsManagerClientTypeAlias = boto3.client("secretsmanager")  # pyright: ignore
asm_client: SecretsManagerClientTypeAlias = boto3.client("secretsmanager")  # pyright: reportGeneralTypeIssues=false, long comment

# output

asm_client: SecretsManagerClient = boto3.client("secretsmanager")  # pyright: ignore[reportUnknownMemberType]
asm_client: SecretsManagerClient = boto3.client(  # pyright: ignore[reportUnknownMemberType]
    "secretsmanager"
)
asm_client: SecretsManagerClientTypeAlias = boto3.client("secretsmanager")  # pyright: ignore
asm_client: SecretsManagerClientTypeAlias = boto3.client(
    "secretsmanager"
)  # pyright: reportGeneralTypeIssues=false, long comment
