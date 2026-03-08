#!/usr/bin/env python3
import csv
import json
import mimetypes
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "data" / "sources.json"
PAPERS_DIR = ROOT / "papers"
REPORTS_DIR = ROOT / "reports"


def safe_name(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def detect_ext(url: str, content_type: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    if path.endswith(".pdf"):
        return ".pdf"
    if "pdf" in (content_type or "").lower():
        return ".pdf"
    guess = mimetypes.guess_extension((content_type or "").split(";")[0].strip())
    if guess:
        return guess
    return ".html"


def main() -> None:
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    report_rows = []

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PathfindingPaperDownloader/1.0)",
        "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
    }

    context = ssl.create_default_context()

    for src in sources:
        src_id = src["id"]
        algorithm = src["algorithm"]
        url = src["url"]
        basename = f"{src_id:02d}_{safe_name(algorithm)}"

        req = urllib.request.Request(url, headers=headers)
        status = "ok"
        message = ""
        saved_path = ""
        content_type = ""

        try:
            with urllib.request.urlopen(req, timeout=45, context=context) as resp:
                data = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                final_url = resp.geturl()
                ext = detect_ext(final_url, content_type)

            outfile = PAPERS_DIR / f"{basename}{ext}"
            outfile.write_bytes(data)
            saved_path = str(outfile.relative_to(ROOT))
            if ext == ".pdf" and not data.startswith(b"%PDF"):
                message = "saved as .pdf but no PDF signature detected"
                status = "warning"
        except urllib.error.HTTPError as e:
            status = "http_error"
            message = f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            status = "url_error"
            message = str(e.reason)
        except Exception as e:
            status = "error"
            message = str(e)

        print(f"[{src_id:02d}] {algorithm}: {status} {saved_path} {message}")
        report_rows.append(
            {
                "id": src_id,
                "algorithm": algorithm,
                "title": src["title"],
                "url": url,
                "status": status,
                "content_type": content_type,
                "saved_path": saved_path,
                "message": message,
            }
        )

    (REPORTS_DIR / "download_report.json").write_text(
        json.dumps(report_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    with (REPORTS_DIR / "download_report.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "algorithm", "status", "content_type", "saved_path", "message", "url"],
        )
        writer.writeheader()
        for row in report_rows:
            writer.writerow({k: row[k] for k in writer.fieldnames})


if __name__ == "__main__":
    main()
