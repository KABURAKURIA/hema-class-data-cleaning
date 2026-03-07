import markdown
from weasyprint import HTML, CSS

def create_pdf(markdown_file, output_file):
    with open(markdown_file, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    # Convert Markdown to HTML using markdown extension to support code blocks
    html_content = markdown.markdown(markdown_text, extensions=['fenced_code', 'codehilite'])

    # Wrap the converted HTML in a structured body for better styling
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hemaclass Data Cleaner Guide</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Highly professional CSS stylesheet for styling the PDF
    css = CSS(string='''
        @page {
            size: A4;
            margin: 20mm;
            @top-right {
                content: "Hemaclass Guide";
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
                color: #777;
            }
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
                color: #777;
            }
        }

        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #333;
            line-height: 1.6;
            font-size: 11pt;
            background-color: #f9f9fc;
        }

        h1 {
            color: #D32F2F;
            font-size: 24pt;
            border-bottom: 2px solid #D32F2F;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }

        h2 {
            color: #1976D2;
            font-size: 18pt;
            margin-top: 30px;
            margin-bottom: 10px;
            border-bottom: 1px solid #1976D2;
        }

        h3 {
            color: #388E3C;
            font-size: 14pt;
            margin-top: 20px;
        }

        p {
            margin-bottom: 15px;
            text-align: justify;
        }

        pre {
            background-color: #2b2b2b;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', Courier, monospace;
            font-size: 10pt;
            page-break-inside: avoid;
        }

        code {
            background-color: #e0e0e0;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 10pt;
            color: #c62828;
        }

        pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
        }

        ul {
            margin-bottom: 15px;
            padding-left: 20px;
        }

        li {
            margin-bottom: 5px;
        }

        hr {
            border: 0;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }
    ''')

    # Use WeasyPrint to generate PDF
    HTML(string=full_html).write_pdf(output_file, stylesheets=[css])
    print(f"✅ Successfully generated {output_file}")

if __name__ == "__main__":
    create_pdf("guide.md", "guide.pdf")
