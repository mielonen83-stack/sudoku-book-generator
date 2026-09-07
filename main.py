import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

def create_sudoku_grid(puzzle_matrix):
    # Muunnetaan 9x9 matriisi ReportLabin Table-yhteensopivaan muotoon
    grid_data = []
    for row in puzzle_matrix:
        formatted_row = [str(cell) if cell != 0 else "" for cell in row]
        grid_data.append(formatted_row)
    
    # Sudokun ruudukon tyylittely
    t = Table(grid_data, colWidths=[20]*9, rowHeights=[20]*9)
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
        ('LINEBELOW', (2,0), (2,-1), 1, colors.black),
        ('LINEBELOW', (5,0), (5,-1), 1, colors.black),
        ('LINERIGHT', (0,2), (-1,2), 1, colors.black),
        ('LINERIGHT', (0,5), (-1,5), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    return t

def build(json_path, pdf_filename, title, subtitle, pagesize):
    doc = SimpleDocTemplate(pdf_filename, pagesize=pagesize,
                            rightMargin=36, leftMargin=36,
                            topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        alignment=1,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        alignment=1,
        spaceAfter=30
    )

    # Kansisivu / Otsikko
    story.append(Spacer(1, 100))
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(PageBreak())

    # Ladataan sudokut JSON-tiedostosta
    with open(json_path, 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    # Lisätään sudokut dokumenttiin (esim. 4 per sivu tai ruudukkoon)
    for p in puzzles:
        story.append(Paragraph(f"Tehtävä #{p['number']} ({p['difficulty']})", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        grid = create_sudoku_grid(p['puzzle'])
        story.append(grid)
        story.append(Spacer(1, 20))
        story.append(PageBreak())

    doc.build(story)

if __name__ == "__main__":
    # Vol 1
    build("puzzles_vol1.json", "kaltiostudio_sudoku_vol1.pdf",
          "KALTIOSTUDIO SUDOKU", "Part 1", A4)
          
    # Vol 2
    build("puzzles_vol2.json", "kaltiostudio_sudoku_vol2.pdf",
          "KALTIOSTUDIO SUDOKU", "Part 2 — 300 New Puzzles", A4)
