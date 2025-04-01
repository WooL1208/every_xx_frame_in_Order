import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from cli.sub_burner_cli import run as sub_burner_cli
        from cli.frame_grabber_cli import run as frame_grabber_cli

        if sys.argv[2] == "burn":
            sub_burner_cli()
        elif sys.argv[2] == "grab":
            frame_grabber_cli()
        else:
            print("未知的 CLI 指令，請使用 'burn' 或 'grab'")
    else:
        from flask import Flask, render_template, request, jsonify
        from app.sub_burner import SubtitleBurner
        from app.frame_grabber import VideoFrameExtractor

        app = Flask(__name__, template_folder="./web/templates")  # 指定模板資料夾

        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/burn")
        def burn():
            return render_template("burn.html", title="燒字幕")

        @app.route("/frames")
        def frames():
            return render_template("frames.html", title="擷取幀")

        @app.route("/run", methods=["POST"])
        def run():
            data = request.json
            burn_subtitles = data.get("burn_subtitles", False)
            grab_frames = data.get("grab_frames", True)
            video_folder = data.get("video_folder", "./data/videos")
            subtitle_folder = data.get("subtitle_folder", "./data/subtitles")
            output_folder = data.get("output_folder", "./data/input")
            font_folder = data.get("font_folder", "./assets/fonts")
            frame_output_folder = data.get(
                "frame_output_folder", "./data/output")
            frame_interval = data.get("frame_interval", 5)
            use_gpu = data.get("use_gpu", True)
            stop_on_error = data.get("stop_on_error", False)
            check_system_fonts = data.get("check_system_fonts", False)
            use_multithreading = data.get("use_multithreading", True)

            if burn_subtitles:
                # 執行燒字幕功能
                burner = SubtitleBurner(
                    video_folder, subtitle_folder, output_folder, font_folder)
                burner.burn_subtitles(
                    use_gpu=use_gpu, stop_on_error=stop_on_error, check_system_fonts=check_system_fonts)

            if grab_frames:
                # 執行擷取幀功能
                extractor = VideoFrameExtractor(
                    output_folder, frame_output_folder)
                extractor.extract_frames(
                    frame_interval=frame_interval, use_multithreading=use_multithreading, use_gpu=use_gpu)

            return jsonify({"status": "success"})

        from waitress import serve
        print("請開啟瀏覽器並前往 http://localhost:7777 使用 GUI")
        serve(app, host="0.0.0.0", port=7777)


if __name__ == "__main__":
    main()
