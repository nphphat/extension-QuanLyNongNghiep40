import sys
import json
import argparse
import os
import io
from app import extract_video_id, get_video_title, get_transcript_text, summarize_text

# Cấu hình API Key Default (Removed)
# DEFAULT_API_KEY = "AIzaSyAOxPM5hG1t0A3U-5yreo7Z9R5qLS9XCDo"

def main():
    parser = argparse.ArgumentParser(description="YouTube API Helper for QuanLyNongNghiep40")
    parser.add_argument("--config", help="Path to JSON config file containing arguments")
    parser.add_argument("--action", choices=["info", "summarize"], help="Action to perform")
    parser.add_argument("--url", help="YouTube Video URL")
    parser.add_argument("--api_key", required=False, help="Gemini API Key")
    parser.add_argument("--model", default="gemini-flash-latest", help="Gemini Model")

    args = parser.parse_args()
    
    # Tải tham số từ file cấu hình nếu có
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config_args = json.load(f)
                # Ghi đè tham số từ file cấu hình
                args.action = config_args.get('action')
                args.url = config_args.get('url')
                args.api_key = config_args.get('api_key', args.api_key)
                args.model = config_args.get('model', args.model)
        except Exception as e:
            # Nếu cấu hình lỗi, xuất lỗi dưới dạng JSON
            print(json.dumps({"success": False, "error": f"Config file error: {str(e)}"}, ensure_ascii=False))
            return

    # Kiểm tra các tham số bắt buộc
    if not args.action or not args.url:
         print(json.dumps({"success": False, "error": "Missing required arguments (action, url)"}, ensure_ascii=False))
         return

    # Tạm thời chặn stdout/stderr để không làm vỡ format JSON
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    result = {"success": False, "data": None, "error": None}

    try:
        if args.action == "info":
            video_id = extract_video_id(args.url)
            if video_id:
                title = get_video_title(args.url)
                result["success"] = True
                result["data"] = {"title": title, "video_id": video_id}
            else:
                result["error"] = "Invalid YouTube URL"

        elif args.action == "summarize":
            video_id = extract_video_id(args.url)
            if video_id:
                transcript, error = get_transcript_text(video_id)
                if transcript:
                    summary = summarize_text(args.api_key, transcript, args.model)
                    result["success"] = True
                    result["data"] = {"summary": summary}
                else:
                     result["error"] = f"Transcript error: {error}"
            else:
                result["error"] = "Invalid YouTube URL"
                
    except Exception as e:
        result["error"] = str(e)
    
    # Khôi phục stdout để in JSON kết quả
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
