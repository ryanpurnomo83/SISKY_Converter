import sys
import re
from docx import Document
from pypdf import PdfReader

QUESTION_RE = re.compile(r"^\s*\d+[.)]\s*(.+)")
OPTION_RE = re.compile(r"^\s*(\*?)([a-zA-Z])[.)]\s*(.+)")

def parse_word(path):
    doc = Document(path)
    return [para.text.strip() for para in doc.paragraphs if para.text.strip()]

def parse_pdf(path):
    reader = PdfReader(path)          # menerima path maupun file.stream
    lines = []
    for page in reader.pages:
        text = page.extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            if line:
                lines.append(line)
    return lines

def to_txt(questions):
    lines = []
    errors = []

    for i, q in enumerate(questions, start=1):
        correct_count = sum(1 for is_correct, _ in q["options"] if is_correct)
        if correct_count == 0:
            errors.append(f"Soal #{i} ('{q['text'][:40]}...') tidak punya jawaban yang ditandai '*'.")
        elif correct_count > 1:
            errors.append(f"Soal #{i} ('{q['text'][:40]}...') punya lebih dari satu jawaban ditandai '*'.")

        opt_lines = [
            f"~%{100 if is_correct else 0}%{opt_text}"
            for is_correct, opt_text in q["options"]
        ]

        lines.append(q["text"])
        # Format persis seperti contoh: '~' baris pertama menempel setelah '{'
        lines.append("{" + (opt_lines[0] if opt_lines else ""))
        lines.extend(opt_lines[1:])
        lines.append("}")
        lines.append("")

    return "\n".join(lines), errors

def convert(lines):
    questions = []
    current_q = None
    
    for text in lines:
        q_match = QUESTION_RE.match(text)
        opt_match = OPTION_RE.match(text)
        
        if opt_match and current_q is not None:
            is_correct = bool(opt_match.group(1))  # ada tanda '*'
            option_text = opt_match.group(3).strip()
            current_q["options"].append((is_correct, option_text))
        elif q_match:
            if current_q is not None:
                questions.append(current_q)
            current_q = {"text": q_match.group(1).strip(), "options": []}
        # baris lain yang tidak cocok pola apa pun akan diabaikan

    if current_q is not None:
        questions.append(current_q)

    return questions


def to_moodle_format(questions):
    lines = []
    errors = []

    for i, q in enumerate(questions, start=1):
        correct_count = sum(1 for is_correct, _ in q["options"] if is_correct)
        if correct_count == 0:
            errors.append(f"Soal #{i} ('{q['text'][:40]}...') tidak punya jawaban yang ditandai '*'.")
        elif correct_count > 1:
            errors.append(f"Soal #{i} ('{q['text'][:40]}...') punya lebih dari satu jawaban ditandai '*'.")

        lines.append(q["text"])
        lines.append("{")
        opt_lines = []
        for is_correct, opt_text in q["options"]:
            pct = 100 if is_correct else 0
            opt_lines.append(f"~%{pct}%{opt_text}")
        # Format persis seperti contoh: '~' baris pertama menempel setelah '{'
        lines[-1] = "{" + opt_lines[0] if opt_lines else "{"
        for extra in opt_lines[1:]:
            lines.append(extra)
        lines.append("}")
        lines.append("")

    return "\n".join(lines), errors


def main():
    if len(sys.argv) != 3:
        print("Pemakaian: python convert_docx_to_moodle_txt.py input.docx output.txt")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]
    raw_lines = parse_word(input_path)
    questions = convert(raw_lines)

    if not questions:
        print("Tidak ada soal yang terdeteksi. Cek format penomoran/opsi di file Word Anda.")
        sys.exit(1)

    output_text, errors = to_txt(questions)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"Berhasil: {len(questions)} soal dikonversi ke '{output_path}' (UTF-8).")

    if errors:
        print("\nPERINGATAN - perlu dicek manual:")
        for e in errors:
            print(" -", e)


if __name__ == "__main__":
    main()