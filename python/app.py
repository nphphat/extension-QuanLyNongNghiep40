import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

def extract_video_id(url):
    """Trích xuất ID video từ URL YouTube"""
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_video_title(url):
    """Lấy tiêu đề của video YouTube"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            match = re.search(r'<title>(.*?)<\/title>', response.text)
            if match:
                title = match.group(1).replace(" - YouTube", "").strip()
                # Xóa các ký tự HTML entity phổ biến
                title = title.replace("&quot;", "\"").replace("&#39;", "'").replace("&amp;", "&")
                return title
    except Exception:
        pass
    return "YouTube Video"

def get_transcript_text(video_id):
    """Lấy nội dung phụ đề của video YouTube"""
    try:
        # Ưu tiên lấy phụ đề tiếng Việt trước, sau đó là tiếng Anh
        transcript_data = YouTubeTranscriptApi().fetch(video_id, languages=['vi', 'en'])
        
        # Ghép các đoạn text lại
        text = " ".join([t.text for t in transcript_data])
        # Loại bỏ các ký tự xuống dòng dính liền
        text = text.replace('\n', ' ')
        return text, None
    except Exception as e:
        return None, f"Không thể lấy được phụ đề cho video này. Chi tiết: {str(e)}"

def summarize_text(api_key, text, model_name="gemini-flash-latest"):
    """Tóm tắt văn bản bằng Gemini API"""
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
Hãy tóm tắt nội dung của đoạn văn bản (nội dung video Youtube) sau một cách chi tiết, chỉ ra các ý chính, mạch lạc và dễ hiểu (Số từ khoảng 100):

{text}
"""
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        return response.text
    except Exception as e:
         return f"Lỗi khi gọi Gemini API: {str(e)}"
