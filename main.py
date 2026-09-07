# main.py
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

DARK = HexColor("#1f2937")
ACCENT = HexColor("#2563eb")
LIGHT_GRID = HexColor("#9ca3af")
BG_SOFT = HexColor("#f3f4f6")

DIFF_COLORS = {
    "Easy": HexColor("#16a34a"),
    "Medium": HexColor("#d97706"),
    "Hard": HexColor("#dc2626"),
    "Very Hard": HexColor("#7c3aed"),
}

DIFF_MAP = {
    "Helppo": "Easy",
    "Keskitaso": "Medium",
    "Vaikea": "Hard",
    "Erittain vaikea": "Very Hard",
}

DIFF_INTRO = {
    "Easy": "A gentle warm-up. Most cells are filled in, so logic alone will get you through quickly.",
    "Medium": "A step up in challenge. You'll need to hold a few candidates in mind at once.",
    "Hard": "Fewer starting clues and trickier deductions. Take your time and look for hidden pairs and pointers.",
    "Very Hard": "The ultimate test. These puzzles demand patience, advanced techniques, and careful notation.",
}


def draw_footer(c, page_num, page_w):
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#9ca3af"))
    c.drawCentredString(page_w / 2, 0.4 * inch, f"KALTIOSTUDIO  \u2022  {page_num}")
    c.setFillColor(black)


def draw_grid(c, puzzle, x0, y0, size, given_color=black, font_size=None):
    cell = size / 9.0
    if font_size is None:
        font_size = cell * 0.55

    c.setLineWidth(1)
    c.setStrokeColor(LIGHT_GRID)
    for i in range(10):
        if i % 3 == 0:
            continue
        x = x0 + i * cell
        c.line(x, y0, x, y0 + size)
        y = y0 + i * cell
        c.line(x0, y, x0 + size, y)

    c.setLineWidth(2.2)
    c.setStrokeColor(DARK)
    for i in range(0, 10, 3):
        x = x0 + i * cell
        c.line(x, y0, x, y0 + size)
        y = y0 + i * cell
        c.line(x0, y, x0 + size, y)

    c.setLineWidth(2.6)
    c.rect(x0, y0, size, size, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(given_color)
    for r in range(9):
        for cnum in range(9):
            v = puzzle[r][cnum]
            if v != 0:
                cx = x0 + cnum * cell + cell / 2
                cy = y0 + (8 - r) * cell + cell / 2 - font_size * 0.35
                c.drawCentredString(cx, cy, str(v))
    c.setFillColor(black)


def cover_page(c, title, subtitle, total, page_w, page_h):
    c.setFillColor(DARK)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setFillColor(HexColor("#111827"))
    band_h = 2.6 * inch
    c.rect(0, page_h - band_h, page_w, band_h, fill=1, stroke=0)

    sample = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],
        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],
        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9],
    ]
    gsize = 1.9 * inch
    gx = (page_w - gsize) / 2
    gy = page_h - band_h + (band_h - gsize) / 2
    c.saveState()
    c.setFillColor(white)
    c.rect(gx - 0.15*inch, gy - 0.15*inch, gsize + 0.3*inch, gsize + 0.3*inch, fill=1, stroke=0)
    draw_grid(c, sample, gx, gy, gsize, given_color=DARK)
    c.restoreState()

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(page_w / 2, page_h - band_h - 0.9*inch, title)

    c.setFont("Helvetica", 16)
    c.setFillColor(HexColor("#d1d5db"))
    c.drawCentredString(page_w / 2, page_h - band_h - 1.35*inch, subtitle)

    badge_text = f"{total} PUZZLES  \u2022  4 DIFFICULTY LEVELS"
    badge_font_size = 14
    text_w = stringWidth(badge_text, "Helvetica-Bold", badge_font_size)
    badge_w = text_w + 0.6*inch
    badge_h = 0.5*inch
    badge_y = page_h - band_h - 2.15*inch
    c.setFillColor(ACCENT)
    c.roundRect(page_w/2 - badge_w/2, badge_y, badge_w, badge_h, 7, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", badge_font_size)
    c.drawCentredString(page_w/2, badge_y + badge_h/2 - badge_font_size*0.35, badge_text)

    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor("#d1d5db"))
    c.drawCentredString(page_w/2, badge_y - 0.55*inch, "Easy  \u2022  Medium  \u2022  Hard  \u2022  Very Hard")

    chip_colors = [DIFF_COLORS["Easy"], DIFF_COLORS["Medium"], DIFF_COLORS["Hard"], DIFF_COLORS["Very Hard"]]
    chip = 0.22*inch
    chip_gap = 0.18*inch
    total_chip_w = 4*chip + 3*chip_gap
    cx0 = page_w/2 - total_chip_w/2
    cy0 = badge_y - 1.0*inch
    for i, col in enumerate(chip_colors):
        c.setFillColor(col)
        c.roundRect(cx0 + i*(chip+chip_gap), cy0, chip, chip, 3, fill=1, stroke=0)

    features = [
        "300 unique, computer-verified puzzles",
        "Progressive difficulty from Easy to Very Hard",
        "One large puzzle per page \u2014 easy on the eyes",
        "Complete answer key included",
        "Optimized for high-quality home printing",
    ]
    box_top = cy0 - 0.6*inch
    box_h = 0.42*inch * len(features) + 0.5*inch
    box_w = 4.6*inch
    box_x = page_w/2 - box_w/2
    box_y = box_top - box_h
    c.setStrokeColor(HexColor("#374151"))
    c.setLineWidth(1)
    c.roundRect(box_x, box_y, box_w, box_h, 8, fill=0, stroke=1)

    fy = box_top - 0.4*inch
    c.setFont("Helvetica", 11.5)
    for feat in features:
        c.setFillColor(ACCENT)
        c.circle(box_x + 0.35*inch, fy + 0.09*inch, 0.05*inch, fill=1, stroke=0)
        c.setFillColor(HexColor("#e5e7eb"))
        c.drawString(box_x + 0.55*inch, fy, feat)
        fy -= 0.42*inch

    c.setFont("Helvetica-Oblique", 10.5)
    c.setFillColor(HexColor("#9ca3af"))
    c.drawCentredString(page_w/2, 0.9*inch, "Full solutions included at the back of the book")

    c.showPage()


def instructions_page(c, page_num, page_w, page_h):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(0.85*inch, page_h - 1.1*inch, "How to Play Sudoku")
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.line(0.85*inch, page_h - 1.25*inch, 2.6*inch, page_h - 1.25*inch)

    body = [
        ("The Goal", "Fill the 9\u00d79 grid so that every row, every column, and every 3\u00d73 "
         "box contains the digits 1 through 9 exactly once."),
        ("The Rules", "Each puzzle starts with some cells already filled in. These are your clues "
         "and can never be changed. Every puzzle in this book has exactly one solution."),
        ("Getting Started", "Look for rows, columns, or boxes that are almost full \u2014 "
         "these are the easiest places to find your next number. Work by elimination: "
         "if a digit already appears in a row, column, or box, it cannot appear again there."),
        ("A Helpful Tip", "For harder puzzles, lightly pencil in small candidate numbers in the "
         "corners of empty cells. As you fill in more of the grid, you can cross out candidates "
         "that are no longer possible."),
        ("Difficulty Levels", "This book is organized into four sections of increasing difficulty: "
         "Easy, Medium, Hard, and Very Hard. Each section begins with more starting clues and "
         "gradually requires more advanced logic."),
        ("Checking Your Work", "Full solutions for every puzzle are printed at the back of the "
         "book, organized by puzzle number, so you can check your answers anytime."),
    ]

    y = page_h - 1.75*inch
    for heading, text in body:
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(ACCENT)
        c.drawString(0.85*inch, y, heading)
        y -= 0.24*inch
        c.setFont("Helvetica", 11)
        c.setFillColor(DARK)
        y = draw_wrapped(c, text, 0.85*inch, y, page_w - 1.7*inch, 14)
        y -= 0.22*inch

    draw_footer(c, page_num, page_w)
    c.showPage()


def draw_wrapped(c, text, x, y, max_width, leading, font="Helvetica", size=11):
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if stringWidth(test, font, size) <= max_width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def toc_page(c, page_num, section_pages, page_w, page_h):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(0.85*inch, page_h - 1.1*inch, "Contents")
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.line(0.85*inch, page_h - 1.25*inch, 2.2*inch, page_h - 1.25*inch)

    y = page_h - 1.9*inch
    c.setFont("Helvetica", 13)
    for label, pg in section_pages:
        c.setFillColor(DARK)
        c.drawString(0.9*inch, y, label)
        c.setFillColor(HexColor("#9ca3af"))
        dots_width = page_w - 1.8*inch - stringWidth(label, "Helvetica", 13) - stringWidth(str(pg), "Helvetica", 13)
        n_dots = max(0, int(dots_width / stringWidth(".", "Helvetica", 13)))
        c.drawString(0.9*inch + stringWidth(label, "Helvetica", 13) + 6, y, "." * n_dots)
        c.setFillColor(DARK)
        c.drawRightString(page_w - 0.9*inch, y, str(pg))
        y -= 0.32*inch

    draw_footer(c, page_num, page_w)
    c.showPage()


def section_divider(c, label, page_num, puzzle_range, page_w, page_h):
    color = DIFF_COLORS[label]
    c.setFillColor(color)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(page_w/2, page_h/2 + 0.6*inch, label)

    c.setFont("Helvetica", 14)
    c.drawCentredString(page_w/2, page_h/2 + 0.15*inch, f"Puzzles {puzzle_range[0]}\u2013{puzzle_range[1]}")

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(HexColor("#ffffff"))
    text = DIFF_INTRO[label]
    draw_wrapped(c, text, 1.3*inch, page_h/2 - 0.5*inch, page_w - 2.6*inch, 16, font="Helvetica-Oblique", size=12)

    draw_footer(c, page_num, page_w)
    c.showPage()


def puzzle_page(c, entry, page_num, page_w, page_h):
    label = entry["difficulty"]
    color = DIFF_COLORS[label]

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(0.85*inch, page_h - 0.95*inch, f"Puzzle #{entry['number']}")

    c.setFillColor(color)
    badge_w = 1.5*inch
    c.roundRect(page_w - 0.85*inch - badge_w, page_h - 1.05*inch, badge_w, 0.32*inch, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(page_w - 0.85*inch - badge_w/2, page_h - 0.95*inch, label.upper())

    c.setStrokeColor(HexColor("#e5e7eb"))
    c.setLineWidth(1)
    c.line(0.85*inch, page_h - 1.15*inch, page_w - 0.85*inch, page_h - 1.15*inch)

    gsize = 5.6 * inch
    gx = (page_w - gsize) / 2
    gy = (page_h - gsize) / 2 - 0.35*inch
    draw_grid(c, entry["puzzle"], gx, gy, gsize)

    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#9ca3af"))
    c.drawCentredString(page_w/2, gy - 0.35*inch, "Notes:")
    c.setStrokeColor(HexColor("#e5e7eb"))
    c.line(gx, gy - 0.55*inch, gx + gsize, gy - 0.55*inch)

    draw_footer(c, page_num, page_w)
    c.showPage()


def solutions_intro(c, page_num, page_w, page_h):
    c.setFillColor(DARK)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(page_w/2, page_h/2 + 0.3*inch, "Solutions")
    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#d1d5db"))
    c.drawCentredString(page_w/2, page_h/2 - 0.15*inch, "Every puzzle, solved \u2014 in order, for easy checking.")
    draw_footer(c, page_num, page_w)
    c.showPage()


def solutions_page(c, entries, page_num, page_w, page_h):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0.7*inch, page_h - 0.7*inch, "Answer Key")
    c.setStrokeColor(HexColor("#e5e7eb"))
    c.line(0.7*inch, page_h - 0.82*inch, page_w - 0.7*inch, page_h - 0.82*inch)

    cols, rows = 3, 3
    margin_x = 0.7*inch
    margin_top = 1.1*inch
    margin_bottom = 0.6*inch
    gap = 0.35*inch

    avail_w = page_w - 2*margin_x - (cols-1)*gap
    avail_h = page_h - margin_top - margin_bottom - (rows-1)*gap
    cell_block_w = avail_w / cols
    cell_block_h = avail_h / rows
    gsize = min(cell_block_w, cell_block_h - 0.3*inch)

    for i, entry in enumerate(entries):
        col = i % cols
        row = i // cols
        bx = margin_x + col * (cell_block_w + gap)
        by_top = page_h - margin_top - row * (cell_block_h + gap)
        label_y = by_top
        gy = label_y - 0.28*inch - gsize
        gx = bx + (cell_block_w - gsize) / 2

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(DARK)
        c.drawCentredString(bx + cell_block_w/2, label_y, f"Puzzle #{entry['number']}")

        draw_grid(c, entry["solution"], gx, gy, gsize, given_color=HexColor("#374151"))

    draw_footer(c, page_num, page_w)
    c.showPage()


def build(puzzles_path, out_path, title, subtitle, pagesize=letter):
    page_w, page_h = pagesize
    with open(puzzles_path, encoding='utf-8') as f:
        data = json.load(f)

    for e in data:
        e["difficulty"] = DIFF_MAP.get(e["difficulty"], e["difficulty"])

    c = canvas.Canvas(out_path, pagesize=pagesize)
    page_num = 1

    cover_page(c, title, subtitle, len(data), page_w, page_h); page_num += 1
    instructions_page(c, page_num, page_w, page_h); page_num += 1

    sections = []
    seen = []
    for e in data:
        if e["difficulty"] not in seen:
            seen.append(e["difficulty"])
    for lab in seen:
        nums = [e["number"] for e in data if e["difficulty"] == lab]
        sections.append((lab, min(nums), max(nums)))

    toc_page_num = page_num
    page_num += 1
    section_start_pages = []
    p = page_num
    for lab, lo, hi in sections:
        section_start_pages.append((f"{lab} Puzzles ({lo}\u2013{hi})", p))
        p += 1 + (hi - lo + 1)
    solutions_start_page = p
    section_start_pages.append(("Solutions", solutions_start_page))

    toc_page(c, toc_page_num, section_start_pages, page_w, page_h)

    for lab, lo, hi in sections:
        section_divider(c, lab, page_num, (lo, hi), page_w, page_h); page_num += 1
        for e in data:
            if e["difficulty"] == lab:
                puzzle_page(c, e, page_num, page_w, page_h); page_num += 1

    solutions_intro(c, page_num, page_w, page_h); page_num += 1
    for i in range(0, len(data), 9):
        chunk = data[i:i+9]
        solutions_page(c, chunk, page_num, page_w, page_h); page_num += 1

    c.save()
    print(f"Saved {out_path} with {page_num-1} pages")


if __name__ == "__main__":
    build("puzzles.json", "kaltiostudio_sudoku_US_Letter.pdf",
          "KALTIOSTUDIO SUDOKU",
          "Easy to Very Hard  \u2014  Created by KALTIOSTUDIO", pagesize=letter)

    build("puzzles.json", "kaltiostudio_sudoku_A4.pdf",
          "KALTIOSTUDIO SUDOKU",
          "Easy to Very Hard  \u2014  Created by KALTIOSTUDIO", pagesize=A4)
