import fitz
from collections import defaultdict
import re

class Data_prep():
    def __init__(self):
        self.blocks =[]
        self.pdf_location = r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\contract_ananlysis\support_docs\petn4-781-exhibits.pdf'
        self.SELECTION_RE = re.compile(
                                            r"^(ARTICLE\s+[IVXLC]+|[0-9]+(\.[0-9]+)*\.?\s+[A-Z][A-Z\s]{3,})$"
                                        )
        self.sections = []

    def _control(self, text):
        text = text.strip()

        # too long → paragraph
        if len(text) > 150:
            return False

        # sentence punctuation → paragraph
        if text.endswith("."):
            return False

        # ARTICLE headings
        if re.match(r"^ARTICLE\s+[IVXLC]+", text, re.I):
            return True

        # Numbered headings
        if re.match(r"^[0-9]+(\.[0-9]+)*\s+[A-Za-z ]+$", text):
            return True

        # ALL CAPS short lines
        if text.isupper() and len(text.split()) <= 10:
            return True

        # Clause keyword fallback
        KEYWORDS = [
            "termination",
            "liability",
            "payment",
            "confidentiality",
            "indemnification",
            "governing law"
        ]
        if any(k in text.lower() for k in KEYWORDS):
            return True

        return False


    def extractblocks(self):
        'extracts text into blocks'
        doc = fitz.open(self.pdf_location)
        for pagenum,page in enumerate(doc,start=1):
            page_dict = page.get_text('dict')
            for block in page_dict['blocks']:
                if block['type'] == 0:
                    text = ''.join(
                        span['text'] for line in block['lines'] for span in line['spans']
                    ).strip()
                    if text:
                        self.blocks.append(
                            {
                                'page':pagenum,
                                'bbox':block['bbox'],
                                'text':text
                            }
                        )

    def buildsections(self):
        current_section = None
        for block in self.blocks:
            text = block['text']
            if self._control(text):
                if current_section:
                    self.sections.append(current_section)
                current_section = {
                    'title':text,
                    'page_start':block['page'],
                    'page_end': block['page'],
                    'text':''
                }
            else:
                if current_section:
                    current_section['text'] += ''+text
                    current_section['page_end'] = block['page']
        
        if current_section:
            self.sections.append(current_section)
    

if __name__ == '__main__':
    obj = Data_prep()
    obj.extractblocks()
    obj.buildsections()
    print(obj.sections)