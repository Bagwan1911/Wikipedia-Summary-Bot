from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def generate_pdf(title, summary, filename="output.pdf"):
    ad = canvas.Canvas(filename, pagesize=A4)

    width, height = A4

    y = height - 50

    # Title - Bold and Big
    ad.setFont("Helvetica-Bold", 20)
    ad.drawString(100, y, title)

    y -= 30

    # Divider line
    ad.setLineWidth(1)
    ad.line(100, y, width - 100, y)

    y -= 30

    # Summary text - Normal
    ad.setFont("Helvetica", 12)

    # Split summary into lines so it fits the page
    words = summary.split()
    line = ""
    for word in words:
        if ad.stringWidth(line + word, "Helvetica", 12) < (width - 200):
            line += word + " "
        else:
            ad.drawString(100, y, line.strip())
            y -= 20
            line = word + " "

            # New page if content goes below
            if y < 50:
                ad.showPage()
                y = height - 50
                ad.setFont("Helvetica", 12)

    if line:
        ad.drawString(100, y, line.strip())

    ad.save()
    return filename