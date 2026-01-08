from io import BytesIO
import fitz  # PyMuPDF

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def certificate(input_pdf, input_blank_pdf, output_pdf, real_name):
    # ---------- STEP 1: FIND <name> ----------
    doc = fitz.open(input_pdf)
    page_fitz = doc[0]

    x0 = y0 = x1 = y1 = font_size = None
    color = (0, 0, 0)

    for block in page_fitz.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if "<name>" in span["text"]:
                    x0, y0, x1, y1 = span["bbox"]
                    font_size = span["size"]

                    c = span["color"]
                    color = (
                        ((c >> 16) & 255) / 255,
                        ((c >> 8) & 255) / 255,
                        (c & 255) / 255
                    )
                    break

    doc.close()

    if x0 is None:
        print("❌ <name> not found")
        return

    # ---------- STEP 2: WRITE TEXT ON BLANK TEMPLATE ----------
    pdf_reader = PdfReader(input_blank_pdf)
    pdf_writer = PdfWriter()
    page = pdf_reader.pages[0]

    packet = BytesIO()
    c = canvas.Canvas(packet)

    pdfmetrics.registerFont(
        TTFont("PinyonScript-Regular", "PinyonScript-Regular.ttf")
    )

    page_height = float(page.mediabox.height)

    # 🔥 AUTO-CENTER LOGIC
    text_width = pdfmetrics.stringWidth(
        real_name,
        "PinyonScript-Regular",
        font_size
    )
    box_width = x1 - x0
    centered_x = x0 + (box_width - text_width) / 2

    # 🔥 BASELINE FIX (THIS IS THE KEY)
    baseline_offset = font_size * 0.25  # tuned for cursive fonts
    correct_y = page_height - y1 + baseline_offset

    c.setFont("PinyonScript-Regular", font_size)
    c.setFillColorRGB(*color)
    c.drawString(centered_x, correct_y, real_name)

    c.save()
    packet.seek(0)

    overlay_page = PdfReader(packet).pages[0]
    page.merge_page(overlay_page)
    pdf_writer.add_page(page)

    for p in pdf_reader.pages[1:]:
        pdf_writer.add_page(p)

    with open(output_pdf, "wb") as f:
        pdf_writer.write(f)

    print("✅ Centered & perfectly aligned certificate generated!")


certificate(
    "template.pdf",
    "template_blank.pdf",
    "output.pdf",
    "Anas Ridwan"
)
