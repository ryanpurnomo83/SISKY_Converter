import os
from flask import Flask, render_template, request
import json 
from pathlib import Path
import converter_moodle as cm

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # batas upload 10 MB
BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "data" / "convertDataType.json", encoding="utf-8") as f:
    FORMAT_MAP = json.load(f)

@app.context_processor
def inject_format_map():
    return {"format_map": FORMAT_MAP}

@app.route("/")
def index():
    return render_template("index.html")

PARSERS = {
    "docx": (".docx", cm.parse_word),
    "word": (".docx", cm.parse_word),
    "pdf" : (".pdf",  cm.parse_pdf)
    # "xml":  (".csv",  cm.parse_xml),
    # "csv":  (".csv",  cm.parse_csv),
    # "xlsx": (".xlsx", cm.parse_excel),
}

RESULTS = {
    "txt" : (".txt", cm.to_txt),
    # "word":  (".word",  cm.to_word),
    # "docx":  (".docx",  cm.to_docx),
    # "pdf":  (".pdf",  cm.to_pdf),
}

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files.get("file")
    docType = request.form.get("doc_type", "")
    fmt = request.form.get("format", "")
    fmt_result = request.form.get("format_result", "")

    if not file or file.filename == "":
        return render_template("index.html", error="Pilih file .docx terlebih dahulu."), 400

    if not file.filename.lower().endswith(".docx"):
        return render_template("index.html", error="Format file harus .docx."), 400

    doc_type = request.form.get("doc_type", "")
    fmt = request.form.get("format", "")          # ← koma diperbaiki
    allowed = [o["value"] for o in FORMAT_MAP.get(doc_type, [])]
    if fmt not in allowed:
        return render_template("index.html", error="Tipe dokumen dan format tidak valid."), 400

    result_options = FORMAT_MAP.get(doc_type + "-result", [])
    if result_options:
        fmt_result = request.form.get("format_result", "")
        if fmt_result not in [o["value"] for o in result_options]:
            return render_template("index.html", error="Format hasil tidak valid."), 400
    
    parser = PARSERS.get(fmt)
    if parser is None:
        return render_template("index.html", error=f"Format '{fmt}' belum didukung."), 400
    
    ext, parse_func = parser
    if not file.filename.lower().endswith(ext):
        return render_template("index.html", error=f"Format file harus {ext}."), 400
    
    try:
        questions = cm.convert(parse_func(file.stream))
    except Exception:
        return render_template(
            "index.html",
            error="File tidak bisa dibaca. Pastikan file adalah dokumen Word (.docx) yang valid.",
        ), 400

    if not questions:
        return render_template(
            "index.html",
            error="Tidak ada soal yang terdeteksi. Cek format penomoran dan pilihan jawaban di file Word Anda.",
        ), 400

    out_ext, write_funct = RESULTS.get(fmt_result, (".txt", cm.to_txt))
    result, warnings = write_funct(questions)
    download_name = os.path.splitext(file.filename)[0] + out_ext

    return render_template(
        "index.html",
        result=result,
        warnings=warnings,
        count=len(questions),
        download_name=download_name,
    )

if __name__ == "__main__":
    app.run(debug=True)