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
  - `opencv-python`
  - `numpy`
  - `tqdm`
  - `pillow`
  - `flask`
  - `flask-cors`

## 安裝方式
1. 確保已安裝 Python 3.8 或以上版本。
2. 安裝所有必要套件：
   ```bash
   pip install fonttools opencv-python numpy tqdm pillow flask flask-cors
   ```
3. 確保系統已安裝 ffmpeg，並將其加入系統環境變數。
   - Windows：從 [ffmpeg 官網](https://ffmpeg.org/download.html) 下載並設定環境變數
   - Linux：使用套件管理器安裝，例如：`sudo apt install ffmpeg`
   - macOS：使用 Homebrew 安裝：`brew install ffmpeg`

## Docker 安裝與使用
### 使用 Docker 執行
1. 確保已安裝 Docker
2. 在專案根目錄執行以下指令建立映像：
   ```bash
   docker build -t every-frame .
   ```
3. 執行容器：
   ```bash
   # Windows PowerShell
   docker run -p 7777:7777 -v ${PWD}/data:/app/data every-frame

   # Linux/macOS
   docker run -p 7777:7777 -v $(pwd)/data:/app/data every-frame
   ```

### Docker 相關說明
- 容器會在 7777 端口提供網頁服務
- 使用 `-v` 參數將本地的 data 目錄掛載到容器中
- 所有的影片、字幕和輸出檔案都會存放在本地的 data 目錄中
- 容器內建已安裝 ffmpeg，無需額外設定

## 使用方式
### 1. 命令列介面 (CLI)
使用命令列執行特定功能：
```bash
# 燒錄字幕
python main.py cli burn

# 提取影片幀
python main.py cli grab
```

### 2. 網頁操作介面
1. 啟動網頁伺服器：
   ```bash
   python main.py
   ```
2. 開啟瀏覽器，訪問 `http://localhost:7777`

#### 主要功能頁面
- **首頁** (`/`): 選擇要使用的功能
- **字幕燒錄** (`/burn`):
  - 上傳影片和字幕檔
  - 選擇字體和編碼設定
  - 調整 GPU 加速選項
  - 檢視處理進度和日誌
- **幀擷取** (`/frames`):
  - 上傳已燒錄字幕的影片
  - 設定擷取間隔
  - 選擇輸出品質
  - 監控處理進度

#### 網頁介面功能說明
1. **檔案管理**
   - 多檔上傳：支援多檔案同時上傳
   - 自動配對：自動匹配影片與字幕檔
   - 檔案檢查：自動驗證檔案格式與完整性

2. **批次處理**
   - 多檔案排程處理
   - 暫停/繼續功能
   - 錯誤自動重試
   - 處理記錄保存

3. **系統設定**
   - 硬體加速設定
   - 輸出品質調整
   - 字體管理
   - 暫存清理

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

## 故障排除
1. **ffmpeg 找不到**
   - 確認 ffmpeg 已正確安裝
   - 檢查系統環境變數是否正確設定
   - 嘗試重新開啟終端機

2. **字幕燒錄失敗**
   - 確認字幕檔編碼為 UTF-8
   - 檢查字幕檔案名稱是否與影片檔案名稱完全相符
   - 確認所需字體檔案存在且可讀取

3. **GPU 加速無效**
   - 確認已安裝 NVIDIA 顯示卡驅動程式
   - 檢查 CUDA 工具包是否正確安裝
   - 確認系統支援 GPU 加速

4. **網頁介面問題**
   - 上傳失敗：檢查檔案大小限制
   - 處理卡住：重新整理頁面
   - 無法連接：確認伺服器狀態
   - 顯示異常：清除瀏覽器快取

## 授權
本專案採用 MIT 授權，詳情請參閱 [LICENSE](LICENSE) 文件。
