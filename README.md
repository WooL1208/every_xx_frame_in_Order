# Every XX Frame in Order

這是一個多功能的影片處理工具，支援以下功能：
1. **字幕燒錄**：將外部字幕檔燒錄到影片中，支援 `.ass` 和 `.srt` 格式。
2. **幀提取**：從影片中提取指定間隔的幀，支援多種影片格式。

## 功能特色
- 支援 GPU 加速，提升處理速度。
- 自動檢查字幕檔所需的字體，避免缺字問題。
- 支援多線程處理，快速處理多個影片檔案。
- 自動建立所需的資料夾，簡化操作流程。

## 環境需求
- Python 3.8 或以上版本
- 已安裝 [ffmpeg](https://ffmpeg.org/)
- 已安裝以下 Python 套件：
  - `fontTools`
  - `concurrent.futures`

## 安裝方式
1. 確保已安裝 Python 3.8 或以上版本。
2. 安裝必要套件：
   ```bash
   pip install fonttools
   ```
3. 確保系統已安裝 ffmpeg，並將其加入系統環境變數。

## 使用方式
### 1. 燒錄字幕到影片
將字幕燒錄到影片中，請確保以下資料夾結構：
```
./videos/          # 放置原始影片
./subtitles/       # 放置字幕檔案 (.ass 或 .srt)
./fonts/           # 放置字體檔案 (.ttf 或 .otf)
./input/           # 燒錄字幕後的影片輸出資料夾
```
執行 `main.py`，並確保 `burn_subtitles` 設為 `True`。

### 2. 提取影片幀
從影片中提取幀，請確保以下資料夾結構：
```
./input/           # 放置燒錄字幕後的影片
./output/          # 提取幀的輸出資料夾
```
執行 `main.py`，並確保 `grab_frames` 設為 `True`。

### 3. 同時執行兩項功能
若需同時執行字幕燒錄與幀提取，請確保上述所有資料夾結構存在，並執行 `main.py`。

## 參數設定
可在 `main.py` 中調整以下參數：
- **字幕燒錄相關參數**
  - `video_folder`：原始影片資料夾路徑。
  - `subtitle_folder`：字幕檔案資料夾路徑。
  - `output_folder`：燒錄字幕後的影片輸出資料夾路徑。
  - `font_folder`：字體檔案資料夾路徑。
  - `video_extension`：影片檔案的副檔名（如 `.mp4`, `.mkv`）。
  - `use_gpu`：是否使用 GPU 加速。
  - `stop_on_error`：遇到錯誤時是否停止。
  - `check_system_fonts`：是否檢查系統字體。

- **幀提取相關參數**
  - `frame_output_folder`：提取幀的輸出資料夾路徑。
  - `frame_interval`：每隔多少幀提取一次。
  - `use_multithreading`：是否使用多線程處理。
  - `use_gpu`：是否使用 GPU 加速。

## 注意事項
1. 確保字幕檔案名稱與影片檔案名稱一致（副檔名除外）。
2. 字體檔案需包含字幕檔中使用的所有字體。
3. 若使用 GPU 加速，請確保系統支援 CUDA 並已安裝相應的驅動程式。

## 授權
本專案採用 MIT 授權，詳情請參閱 [LICENSE](LICENSE) 文件。
