from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

prs = Presentation()

# Title Slide
slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "dZshield Enterprise SOC"
subtitle.text = "7-Layer Architecture: Native Deployment Guide\nAuto-Generated Connectivity Report"

# Slide 1: Local Tool Access Map
slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
title.text = "Local Tool Access Links"
content = slide.placeholders[1].text_frame
content.text = "Here are the URLs to access each module of the architectural matrix:"

p = content.add_paragraph()
p.text = "L7 Web Dashboard: http://localhost:5173"
p.font.bold = True
p.level = 1

p = content.add_paragraph()
p.text = "L6 n8n Orchestrator: http://localhost:5678"
p.font.bold = True
p.level = 1

p = content.add_paragraph()
p.text = "L4/L5 AI / LangGraph Backend API: http://localhost:8000/docs"
p.font.bold = True
p.level = 1

p = content.add_paragraph()
p.text = "L3 Qdrant Vector DB: http://localhost:6333/dashboard"
p.font.bold = True
p.level = 1

# Slide 2: How the Connectivity Works
slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
title.text = "Architecture Modifications (No Docker)"
content = slide.placeholders[1].text_frame
content.text = "Because Windows WSL/Docker is offline, we completely bypassed virtual containers."

p = content.add_paragraph()
p.text = "1. Native OS Qdrant"
p.font.bold = True
p.level = 0
p = content.add_paragraph()
p.text = "We downloaded a raw Windows Executable (qdrant.exe) to store knowledge context without containers."
p.level = 1

p = content.add_paragraph()
p.text = "2. Native OS n8n"
p.font.bold = True
p.level = 0
p = content.add_paragraph()
p.text = "We switched the Orchestrator to run natively on Node.js using 'npx n8n', avoiding the Docker Daemon completely."
p.level = 1

p = content.add_paragraph()
p.text = "3. Auto-Boot Script"
p.font.bold = True
p.level = 0
p = content.add_paragraph()
p.text = "The start_dashboard.bat now explicitly opens 5 native Powershell terminals to run the Web UI, API, log generator, n8n, and Qdrant in pure harmony."
p.level = 1

prs.save('dZshield_Architecture.pptx')
print("PPTX GENERATED SUCCESSFULLY")
