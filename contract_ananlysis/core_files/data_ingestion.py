import fitz
from collections import defaultdict
import re
import uuid
from mongo_control import Mongo_control
from pathlib import Path

class Data_ingestion():
    def __init__(self):

        self.blocks =[]
        self.pdf_location = r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\contract_ananlysis\support_docs\petn4-781-exhibits.pdf'
        self.SELECTION_RE = re.compile(
                                            r"^(ARTICLE\s+[IVXLC]+|[0-9]+(\.[0-9]+)*\.?\s+[A-Z][A-Z\s]{3,})$"
                                        )
        self.ROMAN_RE = re.compile(r"^[IVXLC]+\s+[A-Z][a-zA-Z\s]{3,}$")
        self.NUMBERED_RE = re.compile(r"^[0-9]+\.\s+[A-Z][a-zA-Z\s]{3,}$")
        self.VERBS = {"HAS", "HAVE", "IS", "ARE", "WAS", "WERE", "HELD"}
        self.sections = []
        self.SECTION_MAP = {
                            "TERMINATION": "termination",
                            "PAYMENT": "payment_terms",
                            "CONFIDENTIALITY": "confidentiality",
                            "LIMITATION OF LIABILITY": "liability"
                        }
        self.contractid = None
        self.mongo_obj = Mongo_control() 
        


    def _control(self, text):
        text = text.strip()

        if len(text) > 80:
            return False

        if text.count(" ") > 8:   # <-- KEY LINE
            return False

        if text.endswith("."):
            return False
        
        if any(v in text.upper().split() for v in self.VERBS):
            return False

        return (
            self.SELECTION_RE.match(text)
            or self.ROMAN_RE.match(text)
            or self.NUMBERED_RE.match(text)
            or (text.isupper() and len(text) < 60)
        )
    
    def _normalize_title(self,title:str):
        title = title.upper()
        for i in self.SECTION_MAP:
            if i in title:
                return self.SECTION_MAP[i]
        return 'other'
    
    def _final_object_creation(self,):
        return{
            'contract_id':self.contractid,
            'section':[
                {
                    'section_id':i['section_id'],
                    'title':i['title'],
                    'page_start':i['page_start'],
                    'page_end':i['page_end'],
                    'text':i['text'].strip()
                }for i in self.sections
            ]
        }


    def extractblocks(self):
        'extracts text into blocks'
        doc = fitz.open(self.pdf_location)
        self.contractid = str(uuid.uuid4())
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

    def normalize_text(self):
        for i in self.sections:
            i['section_id'] = self._normalize_title(i['title'])

    def save(self):
        contractobj = self._final_object_creation()
        contractname = Path(self.pdf_location).name
        print(self.mongo_obj.save_contract(contract_obj=contractobj,filename=contractname))

    def run(self):
        self.extractblocks()
        self.buildsections()
        self.normalize_text()
        self.save()
    

if __name__ == '__main__':
    obj = Data_ingestion()
    obj.run()