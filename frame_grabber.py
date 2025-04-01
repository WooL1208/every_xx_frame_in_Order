import os
import subprocess
from concurrent.futures import ThreadPoolExecutor


class VideoFrameExtractor:
    """
    使用 ffmpeg 從影片中提取幀的類別。
    """

    def __init__(self, input_folder: str, output_folder: str):
        """
        初始化 VideoFrameExtractor，設定輸入與輸出資料夾路徑。

        :param input_folder: 包含影片檔案的資料夾路徑。
        :param output_folder: 儲存提取幀的資料夾路徑。
        """
        self.input_folder = input_folder
        self.output_folder = output_folder

        # 確保資料夾存在，若不存在則自動建立
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def extract_frames(self, frame_interval: int = 1, use_multithreading: bool = True, use_gpu: bool = True):
        """
        從輸入資料夾中的所有影片檔案提取幀。

        :param frame_interval: 每隔多少幀提取一次，預設為 1。
        :param use_multithreading: 是否使用多線程處理多個影片，預設為 True。
        :param use_gpu: 是否使用 GPU 編解碼，預設為 True。
        """
        # 確保輸出資料夾存在
        os.makedirs(self.output_folder, exist_ok=True)

        video_files = [
            os.path.join(self.input_folder, video_file)
            for video_file in os.listdir(self.input_folder)
            if os.path.isfile(os.path.join(self.input_folder, video_file)) and self._is_video_file(video_file)
        ]

        if use_multithreading:
            # 使用多線程處理多個影片檔案
            with ThreadPoolExecutor() as executor:
                executor.map(lambda video: self._process_video(
                    video, frame_interval, use_gpu), video_files)
        else:
            # 單線程逐一處理影片檔案
            for video in video_files:
                self._process_video(video, frame_interval, use_gpu)

    def _is_video_file(self, filename: str) -> bool:
        """
        根據副檔名檢查檔案是否為影片。

        :param filename: 檔案名稱。
        :return: 如果是影片則回傳 True，否則回傳 False。
        """
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
        return filename.lower().endswith(video_extensions)

    def _process_video(self, video_path: str, frame_interval: int, use_gpu: bool):
        """
        處理單一影片檔案以提取幀。

        :param video_path: 影片檔案的路徑。
        :param frame_interval: 每隔多少幀提取一次。
        :param use_gpu: 是否使用 GPU 編解碼。
        """
        # 使用 ffprobe 獲取影片的總幀數
        total_frames = self._get_total_frames(video_path)
        if total_frames is None:
            print(f"無法獲取 {video_path} 的總幀數，跳過處理。")
            return

        # 使用 ffprobe 獲取影片的 FPS
        fps = self._get_fps(video_path)
        if fps is None:
            print(f"無法獲取 {video_path} 的 FPS，跳過處理。")
            return

        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_folder = os.path.join(self.output_folder, video_name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 暫存檔案以儲存幀資訊
        info_file = os.path.join(output_folder, "frame_info.txt")

        # 計算實際提取的 FPS
        extract_fps = fps / frame_interval

        # 構建 ffmpeg 命令
        temp_output_pattern = os.path.join(output_folder, "temp_%04d.jpg")
        command = [
            "ffmpeg",
            "-i", video_path,
            f"-vf", f"fps={extract_fps},scale=1920:1080,showinfo",
            "-c:v", "mjpeg",
            "-q:v", "2",
            temp_output_pattern,
            "-vsync", "vfr",
            "-loglevel", "info"
        ]

        if use_gpu:
            # 添加 GPU 編解碼參數
            command.insert(1, "-hwaccel")
            command.insert(2, "cuda")
            command.insert(3, "-c:v")
            command.insert(4, "h264_cuvid")

        process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
        process.communicate()

        # 重新命名輸出的幀檔案
        temp_files = sorted(
            [f for f in os.listdir(output_folder) if f.startswith(
                "temp_") and f.endswith(".jpg")]
        )
        for idx, temp_file in enumerate(temp_files, start=1):
            new_name = f"{video_name}_{idx * frame_interval}_of_{total_frames}.jpg"
            os.rename(
                os.path.join(output_folder, temp_file),
                os.path.join(output_folder, new_name)
            )

        print(f"已提取 {video_path} 的幀。")

    def _parse_frame_info(self, info_file: str, fps: float) -> list:
        """
        解析幀資訊檔案以提取實際幀索引。

        :param info_file: 幀資訊檔案的路徑。
        :param fps: 影片的每秒幀數。
        :return: 實際幀索引的列表。
        """
        frame_indices = []
        with open(info_file, "r") as file:
            for line in file:
                if "pts_time" in line:
                    parts = line.split("pts_time:")
                    if len(parts) > 1:
                        try:
                            pts_time = float(parts[1].split()[0])
                            frame_index = int(round(pts_time * fps))
                            frame_indices.append(frame_index)
                        except ValueError:
                            continue
        return frame_indices

    def _get_fps(self, video_path: str) -> float:
        """
        使用 ffprobe 獲取影片的 FPS。

        :param video_path: 影片檔案的路徑。
        :return: 影片的 FPS，若無法獲取則回傳 None。
        """
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "csv=p=0",
            video_path
        ]
        try:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            fps_str = result.stdout.strip()
            num, den = map(int, fps_str.split('/'))
            return num / den
        except Exception as e:
            print(f"獲取 {video_path} 的 FPS 時發生錯誤：{e}")
            return None

    def _get_total_frames(self, video_path: str) -> int:
        """
        使用 ffprobe 獲取影片的總幀數。

        :param video_path: 影片檔案的路徑。
        :return: 總幀數，若無法獲取則回傳 None。
        """
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-count_frames",
            "-show_entries", "stream=nb_read_frames",
            "-print_format", "csv=p=0",
            video_path
        ]
        try:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            return int(result.stdout.strip())
        except Exception as e:
            print(f"獲取 {video_path} 的總幀數時發生錯誤：{e}")
            return None


if __name__ == "__main__":
    input_folder = "./input"
    output_folder = "./output"

    use_multithreading = True
    use_gpu = True
    frame_interval = 5

    extractor = VideoFrameExtractor(input_folder, output_folder)
    extractor.extract_frames(
        frame_interval=frame_interval, use_multithreading=use_multithreading, use_gpu=use_gpu)
