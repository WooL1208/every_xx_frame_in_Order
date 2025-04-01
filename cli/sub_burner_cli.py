from app.sub_burner import SubtitleBurner


def run():
    # 設定參數
    video_folder = "data/input/"
    subtitle_folder = "data/subtitles/"
    output_folder = "data/output/"
    font_folder = "assets/fonts/"
    use_gpu = True
    stop_on_error = False
    check_system_fonts = False

    # 使用 SubtitleBurner 類別
    burner = SubtitleBurner(video_folder, subtitle_folder,
                            output_folder, font_folder)
    burner.burn_subtitles(
        use_gpu=use_gpu,
        stop_on_error=stop_on_error,
        check_system_fonts=check_system_fonts
    )
