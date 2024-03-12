import os


def dynamodb_table_meta(table_suffix):
    class Meta:
        region = os.getenv("DYNAMODB_REGION", "us-east-1")
        host = os.getenv("DYNAMODB_URL", "http://localhost:8000")
        table_name = f"pynamodb-attributes-{table_suffix}"
        read_capacity_units = 10
        write_capacity_units = 10

    return Meta
