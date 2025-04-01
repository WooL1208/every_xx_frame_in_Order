from sub_burner import process_video_files
from frame_grabber import VideoFrameExtractor


def main():
    # 設定燒錄字幕的參數
    burn_subtitles = True  # 讓使用者選擇燒是否錄字幕
    video_folder = "./videos"
    subtitle_folder = "./subtitles"
    output_folder = "./input"
    font_folder = "./fonts"
    video_extension = ".mkv"
    use_gpu = True
    stop_on_error = False
    check_system_fonts = False

    # 設定提取幀的參數
    grab_frames = True  # 讓使用者選擇是否提取幀
    frame_output_folder = "./output"
    frame_interval = 5
    use_multithreading = True

    if burn_subtitles:
        # 燒錄字幕到影片
        print("開始燒錄字幕到影片...")
        process_video_files(
            original_videos_folder=video_folder,
            subtitle_folder=subtitle_folder,
            output_folder=output_folder,
            font_folder=font_folder,
            video_extension=video_extension,
            use_gpu=use_gpu,
            stop_on_error=stop_on_error,
            check_system_fonts=check_system_fonts
        )

    if grab_frames:
        # 提取影片幀
        print("開始提取影片幀...")
        extractor = VideoFrameExtractor(
            input_folder=output_folder, output_folder=frame_output_folder)
        extractor.extract_frames(
            frame_interval=frame_interval,
            use_multithreading=use_multithreading,
            use_gpu=use_gpu
        )


if __name__ == "__main__":
    main()
