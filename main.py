import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Ei sivunumeroa kansisivulle
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#666666"))
        page_text = f"Sivu {self._pageNumber} / {page_count}"
        self.drawRightString(A4[0] - 36, 25, page_text)
        self.drawString(36, 25, "Kaltiostudio Sudoku Collection")
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(36, 40, A4[0] - 36, 40)
        self.restoreState()

def create_sudoku_grid(puzzle_matrix):
    grid_data = []
    for row in puzzle_matrix:
        formatted_row = [str(cell) if cell != 0 else "" for cell in row]
        grid_data.append(formatted_row)
    
    t = Table(grid_data, colWidths=[24]*9, rowHeights=[24]*9)
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#999999")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#111111")),
        ('LINEBELOW', (2,0), (2,-1), 1.2, colors.HexColor("#111111")),
        ('LINEBELOW', (5,0), (5,-1), 1.2, colors.HexColor("#111111")),
        ('LINERIGHT', (0,2), (-1,2), 1.2, colors.HexColor("#111111")),
        ('LINERIGHT', (0,5), (-1,5), 1.2, colors.HexColor("#111111")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#222222")),
    ]))
    return t

def build_sudoku_book(json_path, pdf_filename, book_title, book_subtitle):
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=A4,
        rightMargin=36, 
        leftMargin=36,
        topMargin=45, 
        bottomMargin=54
    )
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'BookTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        alignment=1,
        textColor=colors.HexColor("#111111"),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'BookSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=15,
        leading=20,
        alignment=1,
        textColor=colors.HexColor("#555555"),
        spaceAfter=40
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#222222"),
        spaceAfter=8
    )

    # --- KANSISIVU ---
    story.append(Spacer(1, 180))
    story.append(Paragraph(book_title, title_style))
    story.append(Paragraph(book_subtitle, subtitle_style))
    story.append(Spacer(1, 60))
    story.append(Paragraph("Kaltiostudio Publishing", ParagraphStyle('Publisher', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=1, textColor=colors.HexColor("#888888"))))
    story.append(PageBreak())

    # --- Ladataan data ---
    with open(json_path, 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    # --- TEHTÄVÄOSIO ---
    story.append(Paragraph("Tehtävät", ParagraphStyle('PartHead', parent=styles['Heading1'], fontSize=20, fontName='Helvetica-Bold', spaceAfter=20)))
    
    for p in puzzles:
        puzzle_elements = [
            Paragraph(f"Tehtävä #{p['number']} &nbsp;|&nbsp; Vaikeustaso: <b>{p['difficulty']}</b>", heading_style),
            Spacer(1, 4),
            create_sudoku_grid(p['puzzle']),
            Spacer(1, 25)
        ]
        story.append(KeepTogether(puzzle_elements))

    story.append(PageBreak())

    # --- RATKAISUOSIO ---
    story.append(Paragraph("Ratkaisut", ParagraphStyle('PartHead2', parent=styles['Heading1'], fontSize=20, fontName='Helvetica-Bold', spaceAfter=20)))
    
    for p in puzzles:
        solution_elements = [
            Paragraph(f"Ratkaisu #{p['number']}", heading_style),
            Spacer(1, 4),
            create_sudoku_grid(p['solution']),
            Spacer(1, 25)
        ]
        story.append(KeepTogether(solution_elements))

    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    build_sudoku_book(
        "puzzles_vol1.json", 
        "kaltiostudio_sudoku_vol1.pdf",
        "KALTIOSTUDIO SUDOKU", 
        "Volume 1 — Klassiset Tehtävät & Ratkaisut"
    )
    
    build_sudoku_book(
        "puzzles_vol2.json", 
        "kaltiostudio_sudoku_vol2.pdf",
        "KALTIOSTUDIO SUDOKU", 
        "Volume 2 — Edistyneet Tehtävät & Ratkaisut"
    )
