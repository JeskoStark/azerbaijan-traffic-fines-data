import csv
import os
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path

import psycopg


def as_decimal(value):
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def main():
    csv_path = Path(os.getenv("CSV_PATH", "/data/fines.csv"))
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(encoding="utf-8-sig", newline="") as source:
        records = list(csv.DictReader(source))

    if not records:
        raise ValueError("CSV contains no data rows")

    expected = {"ixm_maddesi", "pozuntu", "tesvir", "cerime_min_azn", "cerime_max_azn", "cerime_bali", "suruculuk_huququ", "neqliyyat_vasitesi", "resmi_menbe", "sehife_url", "son_yenilenme"}
    missing = expected - set(records[0])
    if missing:
        raise ValueError(f"CSV is missing expected columns: {', '.join(sorted(missing))}")

    conninfo = " ".join([
        f"host={os.getenv('POSTGRES_HOST', 'localhost')}",
        f"port={os.getenv('POSTGRES_PORT', '5432')}",
        f"dbname={os.getenv('POSTGRES_DB', 'fines')}",
        f"user={os.getenv('POSTGRES_USER', 'student')}",
        f"password={os.getenv('POSTGRES_PASSWORD', 'change_me')}",
    ])
    for attempt in range(30):
        try:
            conn = psycopg.connect(conninfo)
            break
        except psycopg.OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)

    with conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS road_fines (
                article TEXT PRIMARY KEY,
                violation TEXT NOT NULL,
                description TEXT,
                fine_min_azn NUMERIC(10,2),
                fine_max_azn NUMERIC(10,2),
                penalty_points INTEGER,
                license_action TEXT,
                vehicle_type TEXT,
                source_url TEXT,
                page_url TEXT,
                last_updated DATE
            )
        """)
        cur.execute("TRUNCATE road_fines")
        insert = """
            INSERT INTO road_fines VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        for row in records:
            cur.execute(insert, (
                row["ixm_maddesi"], row["pozuntu"], row["tesvir"],
                as_decimal(row["cerime_min_azn"]), as_decimal(row["cerime_max_azn"]),
                int(row["cerime_bali"]) if row["cerime_bali"] else None,
                row["suruculuk_huququ"] or None, row["neqliyyat_vasitesi"] or None,
                row["resmi_menbe"] or None, row["sehife_url"] or None,
                row["son_yenilenme"] or None,
            ))
    conn.close()
    print(f"Loaded {len(records)} rows from {csv_path.name} into road_fines")


if __name__ == "__main__":
    main()
