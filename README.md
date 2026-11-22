# GastroFlow

GastroFlow is a restaurant data platform built incrementally with GCP, BigQuery, and dbt.
Start with the existing sample CSVs; keep raw and prepared data local and out of Git.

## Data safety

The sample users CSV is already free of `email` and `password` columns. The preparation
script also removes any CSV column whose name contains `email` or `password` before data
is staged for upload. This is a local, deterministic operation: do not send passwords,
email addresses, or raw user records to an LLM.

## Set up locally (PowerShell)

Run from this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The sample files live under `data\sample\` on this machine and are ignored by Git.
Generate a separate upload-ready copy:

```powershell
python -m collect.prepare_data --input data\sample --output data\ready
```

The script prints filenames and row counts only, not row contents. It fails on malformed
CSV rows instead of silently dropping data. Review the generated files before upload.

## GCP upload (after authentication and bucket setup)

Use Application Default Credentials; do not create or commit service-account key files.

```powershell
gcloud auth login
gcloud auth application-default login
$env:GCS_SOURCE_BUCKET = "your-gastroflow-source-bucket"
python -m collect.upload_to_gcs --directory data\ready --prefix sample/
```

The uploader checks every CSV for email/password columns and checks that the bucket
exists before uploading. It uploads only files directly inside the selected directory.
No GCP resources have been provisioned by this starter project.

## Cost guide

The existing sample is about 90 MB; at an illustrative regional GCS rate of about
$0.02/GB-month, storage is roughly **$0.002/month**. The full dataset is about 2.3 GB,
or roughly **$0.05/month** for GCS storage alone. Actual rates depend on region and
storage class. BigQuery storage, queries, API operations, networking, and any LLM calls
are separate; check the current GCP pricing page and billing estimate for your region.
Use the sample first to validate the pipeline. Avoid always-on services such as Composer
until orchestration is needed.

## Git branches

- `develop` — integration branch.
- `feature/collect-data-parse` — sample preparation and safe upload workflow.

CSV files, virtual environments, credentials, and Terraform state are excluded from Git.
