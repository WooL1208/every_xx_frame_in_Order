from app.frame_grabber import VideoFrameExtractor
from app.sub_burner import process_video_files
from flask import Flask, render_template, request, jsonify


app = Flask(__name__)


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
    video_folder = data.get("video_folder", "data/input/")
    subtitle_folder = data.get("subtitle_folder", "data/subtitles/")
    output_folder = data.get("output_folder", "data/output/")
    font_folder = data.get("font_folder", "assets/fonts/")
    frame_output_folder = data.get(
        "frame_output_folder", "data/output/frames/")
    frame_interval = data.get("frame_interval", 5)
    use_gpu = data.get("use_gpu", True)
    stop_on_error = data.get("stop_on_error", False)
    check_system_fonts = data.get("check_system_fonts", False)
    use_multithreading = data.get("use_multithreading", True)

    if burn_subtitles:
        process_video_files(
            original_videos_folder=video_folder,
            subtitle_folder=subtitle_folder,
            output_folder=output_folder,
            font_folder=font_folder,
            use_gpu=use_gpu,
            stop_on_error=stop_on_error,
            check_system_fonts=check_system_fonts
        )

    if grab_frames:
        extractor = VideoFrameExtractor(
            input_folder=output_folder, output_folder=frame_output_folder)
        extractor.extract_frames(
            frame_interval=frame_interval,
            use_multithreading=use_multithreading,
            use_gpu=use_gpu
        )

    return jsonify({"status": "success"})
