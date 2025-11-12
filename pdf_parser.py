import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

def extract_text_from_pdf(pdf_file_path):
    """
    Extracts text from a local PDF file path or a Streamlit uploaded file object.
    """
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    try:
        if hasattr(pdf_file_path, 'read'):
            fp = pdf_file_path
        else:
            fp = open(pdf_file_path, 'rb')
            
        for page in PDFPage.get_pages(fp, caching=True, check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    finally:
        converter.close()
        fake_file_handle.close()
        if not hasattr(pdf_file_path, 'read'):
              fp.close() 
               
    return text.replace('\n', ' ').replace('\t', ' ')