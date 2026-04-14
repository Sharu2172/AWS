from core.config.loader import get_settings


def get_s3_session():
    try:
        import aioboto3
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "aioboto3 is required to create an AWS session. Install project dependencies before using the S3 client."
        ) from exc

    settings = get_settings()
    aws = settings.aws

    if aws.profile:
        return aioboto3.Session(profile_name=aws.profile)

    return aioboto3.Session(
        aws_access_key_id=aws.access_key,
        aws_secret_access_key=aws.secret_key,
        region_name=aws.region,
    )
