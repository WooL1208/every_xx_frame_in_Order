import subprocess
import os
from fontTools.ttLib import TTFont
import glob


def get_font_name_from_file(font_file):
    """
    從字體檔案中提取字體名稱。

    :param font_file: 字體檔案的路徑。
    :return: 字體名稱，若無法提取則回傳 None。
    """
    try:
        font = TTFont(font_file)
        for record in font['name'].names:
            if record.nameID == 1 and record.platformID == 3:
                return record.string.decode('utf-16-be').strip()
    except Exception:
        pass
    return None


def check_fonts_in_folder(subtitle_file, font_folder):
    """
    檢查字體資料夾中是否包含字幕檔中提到的字體。

    :param subtitle_file: 字幕檔案的路徑。
    :param font_folder: 字體資料夾的路徑。
    :raises RuntimeError: 若缺少必要字體則拋出錯誤。
    """
    try:
        with open(subtitle_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        fonts = set()
        for line in lines:
            if line.startswith("Style:"):
                parts = line.split(",")
                if len(parts) > 1:
                    font_name = parts[1].strip()
                    fonts.add(font_name)

        missing_fonts = []
        for font in fonts:
            font_found = False
            for file in os.listdir(font_folder):
                if file.lower().endswith((".ttf", ".otf")):
                    font_path = os.path.join(font_folder, file)
                    font_file_name = get_font_name_from_file(font_path)
                    if font_file_name and font.lower() == font_file_name.lower():
                        font_found = True
                        break
            if not font_found:
                missing_fonts.append(font)

        if missing_fonts:
            raise RuntimeError(
                f"⚠️ 缺少以下字體，請將它們加入字體資料夾：{', '.join(missing_fonts)}")
        else:
            print("✅ 字體資料夾中包含所有必要的字體。")
    except Exception as e:
        raise RuntimeError(f"❌ 無法檢查字體：{e}")


def burn_subtitles(input_file, output_file, subtitle_file, font_folder, use_gpu=True, stop_on_error=True, check_system_fonts=False):
    """
    使用 ffmpeg 將外部字幕燒錄到影片中，支援多種字幕格式。

    :param input_file: 影片檔案的路徑。
    :param output_file: 輸出影片檔案的路徑。
    :param subtitle_file: 字幕檔案的路徑。
    :param font_folder: 字體資料夾的路徑。
    :param use_gpu: 是否使用 GPU 編解碼。
    :param stop_on_error: 遇到錯誤時是否停止。
    :param check_system_fonts: 是否檢查系統中的字體。
    """
    try:
        subtitle_path = os.path.abspath(subtitle_file).replace("\\", "/")
        font_folder_path = os.path.abspath(font_folder).replace("\\", "/")
        output_path = os.path.abspath(output_file).replace("\\", "/")
        input_path = os.path.abspath(input_file).replace("\\", "/")

        if not os.path.isfile(subtitle_path):
            raise FileNotFoundError(f"字幕檔案不存在或無法讀取：{subtitle_path}")

        if not check_system_fonts and not os.path.isdir(font_folder_path):
            raise FileNotFoundError(f"字體資料夾不存在或無法讀取：{font_folder_path}")

        if not check_system_fonts:
            check_fonts_in_folder(subtitle_path, font_folder_path)

        # 根據字幕檔案副檔名選擇濾鏡
        subtitle_ext = os.path.splitext(subtitle_file)[1].lower()
        if subtitle_ext == ".ass":
            filter_str = f"ass='{subtitle_path.replace(':', r'\:')}'"
        elif subtitle_ext == ".srt":
            filter_str = f"subtitles='{subtitle_path.replace(':', r'\:')}'"
        else:
            raise ValueError(f"不支援的字幕格式：{subtitle_ext}")

        if not check_system_fonts and subtitle_ext == ".ass":
            filter_str += f":fontsdir='{font_folder_path.replace(':', r'\:')}'"

        command = [
            "ffmpeg",
            "-i", input_path,
            "-vf", filter_str,
            "-c:v", "h264_nvenc" if use_gpu else "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "p4" if use_gpu else "medium",
            "-c:a", "copy",
            output_path
        ]

        if use_gpu:
            command.insert(1, "-hwaccel")
            command.insert(2, "cuda")

        subprocess.run(command, check=True)
        print(f"✅ 字幕已成功燒錄到影片中：{output_path}")
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        if stop_on_error:
            raise


def process_video_files(original_videos_folder, subtitle_folder, output_folder, font_folder, video_extension, use_gpu=True, stop_on_error=True, check_system_fonts=False):
    """
    處理資料夾中的所有影片檔案，為每個影片燒錄字幕。

    :param original_videos_folder: 影片資料夾的路徑。
    :param subtitle_folder: 字幕資料夾的路徑。
    :param output_folder: 輸出資料夾的路徑。
    :param font_folder: 字體資料夾的路徑。
    :param video_extension: 影片檔案的副檔名。
    :param use_gpu: 是否使用 GPU 編解碼。
    :param stop_on_error: 遇到錯誤時是否停止。
    :param check_system_fonts: 是否檢查系統中的字體。
    """
    # 確保資料夾存在，若不存在則自動建立
    os.makedirs(original_videos_folder, exist_ok=True)
    os.makedirs(subtitle_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(font_folder, exist_ok=True)

    video_files = glob.glob(os.path.join(
        original_videos_folder, f"*{video_extension}"))

    if not video_files:
        print("資料夾中沒有找到任何符合條件的影片檔案。")
        return

    for video_file in video_files:
        process_single_video(video_file, subtitle_folder, output_folder, font_folder,
                             use_gpu, stop_on_error, check_system_fonts)


def process_single_video(video_file, subtitle_folder, output_folder, font_folder, use_gpu, stop_on_error, check_system_fonts):
    """
    為單一影片檔案燒錄字幕，支援多種字幕格式。

    :param video_file: 影片檔案的路徑。
    :param subtitle_folder: 字幕資料夾的路徑。
    :param output_folder: 輸出資料夾的路徑。
    :param font_folder: 字體資料夾的路徑。
    :param use_gpu: 是否使用 GPU 編解碼。
    :param stop_on_error: 遇到錯誤時是否停止。
    :param check_system_fonts: 是否檢查系統中的字體。
    """
    # 確保輸出資料夾存在
    os.makedirs(output_folder, exist_ok=True)

    # 嘗試匹配字幕檔案
    subtitle_file = None
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    for ext in [".ass", ".srt"]:
        potential_file = os.path.join(subtitle_folder, f"{base_name}{ext}")
        if os.path.exists(potential_file):
            subtitle_file = os.path.abspath(potential_file)
            break

    if not subtitle_file:
        print(f"找不到對應的字幕檔，跳過該影片：{base_name}")
        return

    output_file = os.path.join(output_folder, f"{base_name}_subtitled.mp4")

    try:
        burn_subtitles(video_file, output_file, subtitle_file,
                       font_folder, use_gpu, stop_on_error, check_system_fonts)
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        if stop_on_error:
            raise


if __name__ == "__main__":
    # 參數設定
    original_videos_folder = "./original_videos"
    subtitle_folder = "./subtitles"
    output_folder = "./subtitles_output"
    font_folder = "./fonts"
    video_extension = ".mp4"

    use_gpu = True
    stop_on_error = False
    check_system_fonts = False

    process_video_files(original_videos_folder, subtitle_folder, output_folder, font_folder,
                        video_extension, use_gpu, stop_on_error, check_system_fonts)
