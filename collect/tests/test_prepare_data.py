import csv
import tempfile
import unittest
from pathlib import Path

from collect.prepare_data import prepare_csvs
from collect.upload_to_gcs import validate_csv


class PrepareDataTests(unittest.TestCase):
    def test_removes_email_and_password_before_staging(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = root / "input"
            output_dir = root / "output"
            source_dir.mkdir()
            (source_dir / "users.csv").write_text(
                "user_id,email,password,name\n"
                "7,private@example.com,secret,Sample User\n",
                encoding="utf-8",
            )

            total_rows = prepare_csvs(source_dir, output_dir)

            with (output_dir / "users.csv").open(
                encoding="utf-8", newline=""
            ) as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(total_rows, 1)
            self.assertEqual(rows, [["user_id", "name"], ["7", "Sample User"]])

    def test_malformed_csv_does_not_replace_existing_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = root / "input"
            output_dir = root / "output"
            source_dir.mkdir()
            output_dir.mkdir()
            (source_dir / "users.csv").write_text(
                "user_id,email\n7,private@example.com,unexpected\n",
                encoding="utf-8",
            )
            output_file = output_dir / "users.csv"
            output_file.write_text("user_id\nexisting\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "malformed CSV row"):
                prepare_csvs(source_dir, output_dir)

            self.assertEqual(
                output_file.read_text(encoding="utf-8"), "user_id\nexisting\n"
            )

    def test_uploader_rejects_sensitive_columns(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "users.csv"
            path.write_text("user_id,email\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "sensitive columns"):
                validate_csv(path)


if __name__ == "__main__":
    unittest.main()
