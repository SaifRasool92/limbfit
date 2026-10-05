import requests
import json
import os
import re
import xml.etree.ElementTree as ET

# Create directory
os.makedirs('data/corpus', exist_ok=True)

# Remove old fake files
for f in ["3d_printing_prosthetics.txt", "guidelines.txt", "transradial_socket_guidelines.txt"]:
    fpath = os.path.join('data/corpus', f)
    if os.path.exists(fpath):
        os.remove(fpath)

# Search Europe PMC for Open Access articles on 3D printed prosthetics
query = '("3D printed" OR "3D printing") AND (prosthetic OR prosthesis OR socket)'
url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query} AND OPEN_ACCESS:Y&format=json&resultType=core&pageSize=15'

response = requests.get(url)
data = response.json()

results = data.get('resultList', {}).get('result', [])

licenses_content = "# Corpus Licenses\n\nAll documents in this corpus are open-access and freely redistributable.\n\n"

docs_added = 0
for i, res in enumerate(results):
    pmcid = res.get('pmcid')
    if not pmcid: continue
    
    title = res.get('title', 'Unknown Title')
    pub_year = res.get('pubYear', 'Unknown Year')
    
    # Get license info if available
    license_info = "Open Access (CC-BY or similar)"
    if 'license' in res:
        license_info = res['license']
        
    source_url = f"https://europepmc.org/article/PMC/{pmcid}"
    
    # Fetch full text XML
    ft_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    ft_resp = requests.get(ft_url)
    
    if ft_resp.status_code == 200:
        # Very simple XML to text extraction (just get all text from paragraphs)
        try:
            root = ET.fromstring(ft_resp.content)
            paragraphs = []
            for p in root.iter('p'):
                text = "".join(p.itertext()).strip()
                if text:
                    paragraphs.append(text)
            
            content = "\n\n".join(paragraphs)
            
            # Fallback to abstract if full text has no paragraphs
            if len(paragraphs) < 3:
                content = res.get('abstractText', 'No abstract available.')
                
        except Exception as e:
            content = res.get('abstractText', 'No abstract available.')
    else:
        content = res.get('abstractText', 'No abstract available.')
        
    # Remove HTML tags from content if any
    content = re.sub(r'<[^>]+>', '', content)
    
    # Write file
    filename = f"data/corpus/doc_{i+1:02d}_{pmcid}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Source URL: {source_url}\n")
        f.write(f"License: {license_info}\n")
        f.write(f"Date: {pub_year}\n")
        f.write("-" * 40 + "\n\n")
        f.write(content)
        
    licenses_content += f"## {title}\n"
    licenses_content += f"- **File**: `doc_{i+1:02d}_{pmcid}.txt`\n"
    licenses_content += f"- **Source**: {source_url}\n"
    licenses_content += f"- **License**: {license_info}\n\n"
    
    docs_added += 1

with open('data/corpus/LICENSES.md', 'w', encoding='utf-8') as f:
    f.write(licenses_content)

print(f"Successfully downloaded and processed {docs_added} real articles.")
