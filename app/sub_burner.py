import subprocess
import os
from fontTools.ttLib import TTFont
from tqdm import tqdm
import sys  # 新增
import glob
import re  # 新增


class SubtitleBurner:
    """
    使用 ffmpeg 將字幕燒錄到影片中的類別。
    """

    def __init__(self, original_videos_folder: str, subtitle_folder: str, output_folder: str, font_folder: str):
        """
        初始化 SubtitleBurner，設定資料夾路徑。

        :param original_videos_folder: 影片資料夾的路徑。
        :param subtitle_folder: 字幕資料夾的路徑。
        :param output_folder: 輸出資料夾的路徑。
        :param font_folder: 字體資料夾的路徑。
        """
        self.original_videos_folder = original_videos_folder
        self.subtitle_folder = subtitle_folder
        self.output_folder = output_folder
        self.font_folder = font_folder

        # 確保資料夾存在，若不存在則自動建立
        os.makedirs(self.original_videos_folder, exist_ok=True)
        os.makedirs(self.subtitle_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.font_folder, exist_ok=True)

    def burn_subtitles(self, use_gpu: bool = True, stop_on_error: bool = True, check_system_fonts: bool = False):
        """
        處理資料夾中的所有影片檔案，為每個影片燒錄字幕。

        :param use_gpu: 是否使用 GPU 編解碼。
        :param stop_on_error: 遇到錯誤時是否停止。
        :param check_system_fonts: 是否檢查系統中的字體。
        """
        supported_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"]

        video_files = [
            file for file in glob.glob(os.path.join(self.original_videos_folder, "*"))
            if os.path.splitext(file)[1].lower() in supported_extensions
        ]

        if not video_files:
            raise RuntimeError("資料夾中沒有找到任何符合條件的影片檔案。")

        with tqdm(video_files, file=sys.stdout) as progress_bar:  # 指定輸出流
            for video_file in progress_bar:
                progress_bar.set_description(
                    f"處理影片: {os.path.basename(video_file)}")
                self._process_single_video(
                    video_file, use_gpu, stop_on_error, check_system_fonts)

    def _process_single_video(self, video_file: str, use_gpu: bool, stop_on_error: bool, check_system_fonts: bool):
        """
        為單一影片檔案燒錄字幕。

        :param video_file: 影片檔案的路徑。
        :param use_gpu: 是否使用 GPU 編解碼。
        :param stop_on_error: 遇到錯誤時是否停止。
        :param check_system_fonts: 是否檢查系統中的字體。
        """
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        subtitle_file = None
        for ext in [".ass", ".srt"]:
            potential_file = os.path.join(
                self.subtitle_folder, f"{base_name}{ext}")
            if os.path.exists(potential_file):
                subtitle_file = os.path.abspath(potential_file)
                break

        if not subtitle_file:
            print(f"找不到對應的字幕檔，跳過該影片：{base_name}")
            return

        output_file = os.path.join(
            self.output_folder, f"{base_name}_subtitled.mp4")

        try:
            with tqdm(total=100, desc=f"燒錄進度: {os.path.basename(video_file)}", file=sys.stdout) as progress_bar:
                self._burn_subtitles_to_video(
                    video_file, output_file, subtitle_file, use_gpu, stop_on_error, check_system_fonts, progress_bar)
        except Exception as e:
            print(f"❌ 發生錯誤：{e}")
            if stop_on_error:
                raise

    def _burn_subtitles_to_video(self, input_file: str, output_file: str, subtitle_file: str, use_gpu: bool, stop_on_error: bool, check_system_fonts: bool, progress_bar=None):
        """
        使用 ffmpeg 將外部字幕燒錄到影片中。

        :param input_file: 影片檔案的路徑。
        :param output_file: 輸出影片檔案的路徑。
        :param subtitle_file: 字幕檔案的路徑。
        :param use_gpu: 是否使用 GPU 編解碼。
        :param stop_on_error: 遇到錯誤時是否停止。
        :param check_system_fonts: 是否檢查系統中的字體。
        :param progress_bar: 進度條物件。
        """
        subtitle_path = os.path.abspath(subtitle_file).replace("\\", "/")
        font_folder_path = os.path.abspath(self.font_folder).replace("\\", "/")
        output_path = os.path.abspath(output_file).replace("\\", "/")
        input_path = os.path.abspath(input_file).replace("\\", "/")

        if not os.path.isfile(subtitle_path):
            raise FileNotFoundError(f"字幕檔案不存在或無法讀取：{subtitle_path}")

        if not check_system_fonts and not os.path.isdir(font_folder_path):
            raise FileNotFoundError(f"字體資料夾不存在或無法讀取：{font_folder_path}")

        if not check_system_fonts:
            self._check_fonts_in_folder(subtitle_path)

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

        try:
            # 直接取得影片總時長
            probe_command = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                input_file
            ]
            try:
                total_duration_str = subprocess.check_output(
                    probe_command, encoding="utf-8").strip()
                if total_duration_str == "N/A" or not total_duration_str:
                    raise ValueError("無法取得影片總時長")
                total_duration = float(total_duration_str)
                if total_duration <= 0:
                    raise ValueError("影片總時長無效")
                total_frames = int(total_duration * 30)  # 假設每秒 30 幀
            except (subprocess.CalledProcessError, ValueError):
                raise RuntimeError(f"無法取得影片總時長，請檢查檔案是否損壞或格式不支援：{input_file}")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                encoding="utf-8"  # 強制使用 UTF-8 編碼
            )

            # 正規表達式解析幀數
            frame_pattern = re.compile(r'frame=\s*(\d+)')

            with tqdm(total=total_frames, desc=f"燒錄進度: {os.path.basename(input_file)}", unit="frame(s)", file=sys.stdout) as progress_bar:
                for stderr_line in process.stderr:
                    match = frame_pattern.search(stderr_line)
                    if match:
                        current_frame = int(match.group(1))
                        progress_bar.n = current_frame
                        progress_bar.refresh()

                process.wait()

                if process.returncode != 0:
                    raise RuntimeError(f"ffmpeg 執行失敗，錯誤碼：{process.returncode}")

            print(f"\n✅ 字幕已成功燒錄到影片中：{output_path}")

        except Exception as e:
            print(f"\n❌ 發生錯誤：{e}")
            if stop_on_error:
                raise

        # 檢查輸出檔案是否成功生成
        if not os.path.exists(output_path):
            raise RuntimeError(f"❌ 輸出檔案未生成：{output_path}")

    def _check_fonts_in_folder(self, subtitle_file: str):
        """
        檢查字體資料夾中是否包含字幕檔中提到的字體。

        :param subtitle_file: 字幕檔案的路徑。
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
                for file in os.listdir(self.font_folder):
                    if file.lower().endswith((".ttf", ".otf")):
                        font_path = os.path.join(self.font_folder, file)
                        font_file_name = self._get_font_name_from_file(
                            font_path)
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

    def _get_font_name_from_file(self, font_file: str) -> str:
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


if __name__ == "__main__":
    original_videos_folder = "./original_videos"
    subtitle_folder = "./subtitles"
    output_folder = "./subtitles_output"
    font_folder = "./fonts"

    use_gpu = True
    stop_on_error = False
    check_system_fonts = False

    burner = SubtitleBurner(original_videos_folder,
                            subtitle_folder, output_folder, font_folder)
    burner.burn_subtitles(use_gpu=use_gpu, stop_on_error=stop_on_error,
                          check_system_fonts=check_system_fonts)
