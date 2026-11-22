"""Upload safe CSVs to an existing GCS bucket using Application Default Credentials."""

import argparse
import csv
import os
from pathlib import Path


def validate_csv(path: Path) -> None:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream), None)
    if not header:
        raise ValueError(f"CSV has no header: {path.name}")
    sensitive = [
        column
        for column in header
        if "email" in column.casefold() or "password" in column.casefold()
    ]
    if sensitive:
        raise ValueError(
            f"Refusing to upload {path.name}; sensitive columns are present."
        )


def upload_csvs(bucket_name: str, directory: Path, prefix: str) -> int:
    from google.cloud import storage

    source_dir = directory.resolve()
    if not source_dir.is_dir():
        raise FileNotFoundError(f"CSV directory does not exist: {source_dir}")
    files = sorted(source_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {source_dir}")

    for path in files:
        validate_csv(path)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        raise FileNotFoundError(f"GCS bucket gs://{bucket_name} does not exist.")

    object_prefix = prefix.strip("/")
    for path in files:
        object_name = f"{object_prefix}/{path.name}" if object_prefix else path.name
        bucket.blob(object_name).upload_from_filename(
            str(path), content_type="text/csv"
        )
        print(f"Uploaded {path.name} to gs://{bucket_name}/{object_name}")
    return len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", default=os.environ.get("GCS_SOURCE_BUCKET"))
    parser.add_argument("--directory", type=Path, default=Path("data/ready"))
    parser.add_argument("--prefix", default="sample/")
    args = parser.parse_args()
    if not args.bucket:
        parser.error("--bucket or GCS_SOURCE_BUCKET is required")
    count = upload_csvs(args.bucket, args.directory, args.prefix)
    print(f"Uploaded {count} CSV file(s) to gs://{args.bucket}/{args.prefix.strip('/')}/")


if __name__ == "__main__":
    main()
