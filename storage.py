"""Azure Blob Storage upload."""

import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

# Hardcoded config
DEFAULT_CONTAINER = "aigeneratedpodcast"
BLOB_BASE_URL = "https://birkspublic.blob.core.windows.net/aigeneratedpodcast"


def upload_blob(local_path: Path, blob_name: str | None = None) -> str:
    """
    Upload a file to Azure Blob Storage.

    Returns the public URL of the uploaded blob.
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set in environment")

    container = os.getenv("AZURE_CONTAINER_NAME", DEFAULT_CONTAINER)

    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")

    # Use filename as blob name if not specified
    if blob_name is None:
        blob_name = local_path.name

    print(f"Uploading to Azure Blob Storage...")
    print(f"  Container: {container}")
    print(f"  Blob name: {blob_name}")

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(
        container=container,
        blob=blob_name,
    )

    with open(local_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)

    url = f"{BLOB_BASE_URL}/{blob_name}"
    print(f"  URL: {url}")

    return url
