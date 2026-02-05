from google import genai
from google.genai import types
import pypandoc
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("setup api key trong .env")

client = genai.Client(api_key=api_key) 

def ocr_bytes_to_markdown(image_bytes: bytes) -> str:
    prompt = """
    Bạn là OCR engine, phiên dịch viên chuyên nghiệp.
    Hãy đọc toàn bộ nội dung trong ảnh và trả về kết quả ở dạng Markdown.
    Đảm bảo các quy tắc sau:
    1. Văn bản thường giữ nguyên.
    2. Dịch văn bản qua tiếng việt và giữ lại 1 số từ ngữ chuyên ngành ở tiếng anh, chú ý ngữ nghĩa sao cho trôi chảy
    3. Bảng phải được định dạng chính xác theo cú pháp Markdown table (| col1 | col2 |).
    4. Công thức toán học (equations) phải được bao quanh bởi dấu đô la:
       - Inline math: `$equation$` (ví dụ: $E=mc^2$)
       - Display block math: `$$equation$$` trên một dòng riêng biệt (ví dụ: $$\sum_{i=0}^n i^2 = \frac{n(n+1)(2n+1)}{6}$$)
    5. Mỗi công thức toán học (equation) cần phải tách riêng ra 1 dòng.
    6. KHÔNG thêm bất kỳ giải thích nào, chỉ xuất ra Markdown hợp lệ.
    7. Khi ocr loại bỏ các kí tự đặc biệt của file .md trừ $ hoặc |, loại bỏ `
    8. ĐẶC BIỆT Lưu ý, chỉ xuất tiếng Việt.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt
        ]
    )

    return response.text.strip()

def markdown_to_docx(md_text: str, out_path: str):
    try:
        pypandoc.convert_text(
            md_text,
            to='docx',
            format='markdown+tex_math_dollars+tex_math_single_backslash-yaml_metadata_block',
            outputfile=out_path,
            extra_args=[
                '--standalone',
                '--mathml'
            ]
        )
    except Exception as e:
        raise RuntimeError(f"Pandoc DOCX conversion failed: {e}")



def markdown_to_pdf(md_text: str, out_path: str):
    try:
        pypandoc.convert_text(
            md_text,
            'pdf',
            format='markdown+tex_math_dollars+tex_math_single_backslash-yaml_metadata_block',
            outputfile=out_path,
            extra_args=[
                '--standalone',
                '--pdf-engine=xelatex'
            ]
        )
    except Exception as e:
        raise RuntimeError(f"Pandoc PDF conversion failed: {e}")
