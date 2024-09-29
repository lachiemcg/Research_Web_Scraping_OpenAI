import os
import json
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Paths
input_dir = "openai_responses"
output_dir = "Generated_Reports"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Set up styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Heading', fontSize=18, spaceAfter=12, leading=22))
styles.add(ParagraphStyle(name='SubHeading', fontSize=14, spaceAfter=10, leading=18))

# Iterate over all JSON files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        # Construct file paths
        input_json_path = os.path.join(input_dir, filename)
        output_pdf_name = filename.replace(".json", ".pdf")
        output_pdf_path = os.path.join(output_dir, output_pdf_name)

        # Load the JSON data
        with open(input_json_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Create a PDF document
        doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
        elements = []

        # Use the JSON filename (without extension) as the report title
        report_title = filename.replace(".json", "").replace("_", " ").title()
        elements.append(Paragraph(report_title, styles['Heading']))
        elements.append(Spacer(1, 0.2 * inch))

        # Add each section from the JSON
        for section, content in data.items():
            section_title = section.replace('_', ' ').title()
            elements.append(Paragraph(section_title, styles['SubHeading']))
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)  # Embed links properly
            elements.append(Paragraph(content, styles['BodyText']))
            elements.append(Spacer(1, 0.2 * inch))

        # Build the PDF
        doc.build(elements)
        print(f"PDF report generated and saved to: {output_pdf_path}")

