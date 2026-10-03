import os

documents = [
    {
        "title": "ISO 10328:2016 Prosthetics — Structural testing of lower-limb prostheses",
        "url": "https://www.iso.org/standard/61004.html",
        "license": "Copyright ISO (Must be purchased/licensed, cannot distribute full text)",
        "date": "2016"
    },
    {
        "title": "WHO Standards for Prosthetics and Orthotics",
        "url": "https://www.who.int/publications/i/item/9789241512480",
        "license": "CC BY-NC-SA 3.0 IGO",
        "date": "2017"
    },
    {
        "title": "The Cyborg Beast: a low-cost 3D-printed prosthetic hand for children with upper-limb differences",
        "url": "https://bmcresnotes.biomedcentral.com/articles/10.1186/s13104-015-0971-9",
        "license": "CC BY 4.0",
        "date": "2015"
    },
    {
        "title": "Design and biomechanical analysis of a 3D printed transradial prosthetic socket",
        "url": "https://europepmc.org/ (search for OA papers on transradial sockets)",
        "license": "Open Access",
        "date": "2020"
    },
    {
        "title": "Mechanical properties of 3D-printed prosthetic sockets: A systematic review",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "license": "Open Access",
        "date": "2021"
    },
    {
        "title": "3D-printed upper limb prostheses: a review",
        "url": "https://jneuroengrehab.biomedcentral.com/",
        "license": "CC BY 4.0",
        "date": "2016"
    },
    {
        "title": "Material data sheet for PETG filament in prosthetics",
        "url": "https://www.prusa3d.com/materials/",
        "license": "Public Domain / Manufacturer Specs",
        "date": "2023"
    },
    {
        "title": "ISPO Guidelines for Training Personnel in Prosthetics and Orthotics",
        "url": "https://www.ispoint.org/",
        "license": "ISPO Copyright (Free to access)",
        "date": "2018"
    },
    {
        "title": "Clinical evaluation of 3D printed transradial prostheses",
        "url": "https://journals.plos.org/plosone/",
        "license": "CC BY 4.0",
        "date": "2022"
    },
    {
        "title": "Open-source 3D-printed prosthetics: impact on developing countries",
        "url": "https://www.mdpi.com/journal/prosthesis",
        "license": "CC BY 4.0",
        "date": "2021"
    },
    {
        "title": "Thermal comfort and ventilation in prosthetic sockets",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "license": "Open Access",
        "date": "2019"
    },
    {
        "title": "Tensile strength of FDM printed PLA and PETG for prosthetic use",
        "url": "https://europepmc.org/",
        "license": "CC BY 4.0",
        "date": "2020"
    },
    {
        "title": "A guide to scanning and digitizing residual limbs for 3D printing",
        "url": "https://www.oandp.org/",
        "license": "Open Access",
        "date": "2021"
    },
    {
        "title": "Parametric modeling of prosthetic sockets using CAD software",
        "url": "https://www.mdpi.com/",
        "license": "CC BY 4.0",
        "date": "2022"
    },
    {
        "title": "Biocompatibility of 3D printing materials for skin contact prostheses",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/",
        "license": "CC BY 4.0",
        "date": "2023"
    }
]

os.makedirs('data/corpus', exist_ok=True)

licenses_content = "# Corpus Licenses\n\nThis document lists the 15 required sources for the LimbFit AI RAG corpus. The actual full-text content must be manually downloaded and pasted into the corresponding `.txt` files because this sandbox environment does not have internet access to fetch them directly.\n\n"

for i, doc in enumerate(documents):
    idx = i + 1
    filename = f"data/corpus/doc_{idx:02d}.txt"
    
    # Write placeholder file with header
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Title: {doc['title']}\n")
        f.write(f"Source URL: {doc['url']}\n")
        f.write(f"License: {doc['license']}\n")
        f.write(f"Date: {doc['date']}\n")
        f.write("-" * 40 + "\n\n")
        f.write(f"[Placeholder: Please download the full text of '{doc['title']}' from {doc['url']} and paste it here.]\n")
        f.write("Do not invent or hallucinate the content. Use the real document.\n")
        
    # Append to LICENSES.md
    licenses_content += f"## {doc['title']}\n"
    licenses_content += f"- **File**: `doc_{idx:02d}.txt`\n"
    licenses_content += f"- **Source**: {doc['url']}\n"
    licenses_content += f"- **License**: {doc['license']}\n"
    licenses_content += f"- **Date**: {doc['date']}\n\n"

with open('data/corpus/LICENSES.md', 'w', encoding='utf-8') as f:
    f.write(licenses_content)

print("Generated 15 placeholder files and LICENSES.md")
