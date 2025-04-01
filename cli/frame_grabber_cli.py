from app.frame_grabber import VideoFrameExtractor


def run():
    # 設定參數
    input_folder = "data/input/"
    output_folder = "data/output/frames/"
    frame_interval = 5
    use_multithreading = True
    use_gpu = True

    extractor = VideoFrameExtractor(input_folder, output_folder)
    extractor.extract_frames(
        frame_interval=frame_interval,
        use_multithreading=use_multithreading,
        use_gpu=use_gpu
    )
