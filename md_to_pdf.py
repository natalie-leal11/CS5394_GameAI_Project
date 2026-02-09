"""
Convert Markdown (.md) files to PDF.
Uses markdown + weasyprint for a pure Python solution.
"""

import markdown
from weasyprint import HTML
from pathlib import Path


def md_to_pdf(md_path: str, pdf_path: str | None = None) -> None:
    """Convert a Markdown file to PDF."""
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    pdf_path = Path(pdf_path or md_path.with_suffix(".pdf"))

    # Read and convert Markdown to HTML
    md_content = md_path.read_text(encoding="utf-8")
    html_content = markdown.markdown(
        md_content,
        extensions=["extra", "codehilite", "toc", "tables"],
    )

    # Wrap in basic HTML structure for better styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Georgia, serif; line-height: 1.6; margin: 2em; }}
            code {{ background: #f4f4f4; padding: 0.2em 0.4em; border-radius: 3px; }}
            pre {{ background: #f4f4f4; padding: 1em; overflow-x: auto; }}
            h1, h2, h3 {{ color: #333; }}
        </style>
    </head>
    <body>{html_content}</body>
    </html>
    """

    HTML(string=full_html, base_url=str(md_path.parent)).write_pdf(pdf_path)
    print(f"Created: {pdf_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <input.md> [output.pdf]")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None
    md_to_pdf(md_file, pdf_file)