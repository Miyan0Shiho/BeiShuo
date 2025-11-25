## 目标
- 接入看典古籍 `https://ocr.kandianguji.com/ocr_api`，在后端完成调用与结果解析。
- 在现有“识别”页面实现图片上传→识别→结果查看→详细校对的完整流程，并支持参数配置（版面识别、候选字、坐排方向等）。

## 后端实现
- 路由改造（保持命名空间 `/api/v1/recognition`）
  - 编辑 `python/app/api/v1/recognition.py`：
    - 在 `start_recognition` 增加对 `image_url` 与 `image_base64` 的支持；若传 `image_url`，从 `settings.file_upload_path` 读文件并转为 Base64；若传 `image_base64`，直接使用。
    - 将当前占位逻辑替换为调用 OCR 客户端并同步返回识别结果；保留 `task_id` 字段以兼容前端进度 UI，但状态为 `completed`。
    - 解析外部 API 响应的 `data` 字段，组装统一返回：
      - `text`（拼接文本行）、`word_count`、`confidence`（均值/最小值二选一，优先均值）、`width`、`height`、`text_angel`、`texts`、`text_lines`（含坐标、候选字、置信度等）。
    - `correct_recognition` 保持不变，接受 `corrected_text` 与 `corrections`（可选，包含 {position/index, old, new}）。
  - 上传路由沿用：`python/app/api/v1/upload.py`（已存在），无需新增路由。
- 新增 OCR 客户端（必要新增文件）
  - `python/app/client/kandianguji_ocr_client.py`：
    - 使用 `httpx` POST 调用 `https://ocr.kandianguji.com/ocr_api`，支持 JSON 或 FormData，默认 JSON。
    - 参数映射：`token`、`email`、`image`、`char_ocr`、`det_mode`、`image_size`、`return_position`、`return_choices`、`version`、`det_layout`、`only_plain_text`、`return_layout`、`auto_insert_space`、`hp_line_words_angel`、`sp_line_words_angel`。
    - 响应模型：校验 `message === 'success'`，返回 `data`；失败时抛业务异常并携带 `info`。
  - 可选服务封装：`python/app/services/ocr_service.py`（若需要）：负责图片读取/编码、请求参数默认值与结果归一化。
- 配置
  - 在 `app/config.py` 增加可选配置项（读取环境变量）：
    - `kandianguji_ocr_token`、`kandianguji_ocr_email`、`kandianguji_ocr_timeout`（默认 15000ms）。
  - 禁止硬编码密钥；部署环境注入 `.env`：
    - `KANDIANGUJI_OCR_TOKEN=c6204f29-da89-4e36-8762-8fc1528f89d2`
    - `KANDIANGUJI_OCR_EMAIL=13764120319`

## 前端实现
- 识别页面 `frontend/src/views/Recognition.vue`
  - 上传弹窗已具备 UI；在 `confirmUpload`：
    - 先调用后端 `POST /api/v1/upload/image` 上载文件，获得 `image_url`。
    - 其后调用 `POST /api/v1/recognition/start`，请求体含 `image_url` 与参数配置（提供基础表单：`det_mode`、`return_position`、`return_choices`、`version`、`det_layout`、`only_plain_text`、`return_layout`、`hp_line_words_angel`、`sp_line_words_angel`）。
    - 识别期间维持现有进度条；完成后用真实返回填充 `recognitionResult`（`text`、`wordCount`、`confidence`、`time` 等），并缓存 `recognition_id` 与结构化的 `text_lines/words`。
  - 详细校对页：
    - 使用返回的 `text_lines.words` 渲染逐字/逐行校对；保留现有弹窗交互，候选字来源于 `choices`。
    - “保存校对结果”按钮调用 `PUT /api/v1/recognition/{recognition_id}/correct`，提交 `corrected_text`（合成后的全文）与 `corrections`（用户改动列表）。
  - AI阐释页沿用既有逻辑，输入 `recognitionResult.text` 触发。
- 前端 API 封装
  - 在 `frontend/src/api/ai.js` 中新增：
    - `uploadImage({ baseUrl, token, file })`→`/upload/image`
    - `startRecognition({ baseUrl, token, imageUrl, imageBase64, options })`→`/recognition/start`

## 数据结构与映射
- 外部响应到内部：
  - `text`：按 `texts` 或 `text_lines[*].text` 拼接；
  - `wordCount`：累计 `words` 数；
  - `confidence`：`words[*].confidence` 平均值；
  - `positions`：保留 `text_lines.position` 与 `words.position`（用于高亮/定位）。
  - `layout`：当 `return_layout` 为 True 时展示版面信息。
- 识别 ID：生成 `rec_<timestamp>` 或由外部 `id` 映射；与校对接口保持一致。

## 错误处理与兼容
- 明确使用 `POST` 方法避免 405；`Content-Type: application/json`。
- 失败时前端气泡提示 `message` 与 `info`；后端记录 `logger.error` 并返回 `Result.fail`。
- 参数默认：`version: 'v2'`、`det_mode: 'auto'`、`return_position: true`、`return_choices: false`、`det_layout: false`。

## 验证流程
- 本地启动已有前端开发服务器（已在运行）。
- 在识别页执行：上传任意清晰样例图片→识别→查看结果与详细校对→保存校对→AI阐释。
- 观察网络请求：`/upload/image`、`/recognition/start` 成功，响应含文本与坐标；校对保存 `200`。

## 变更点（代码导航）
- 后端：
  - `python/app/api/v1/recognition.py:13-36`（start_recognition：改为实际调用并返回结果）
  - 新增：`python/app/client/kandianguji_ocr_client.py`（仅此必要新增）
  - 可选新增：`python/app/services/ocr_service.py`
- 前端：
  - `frontend/src/views/Recognition.vue`（`confirmUpload`、`startRecognition` 接入真实 API 与结果渲染）
  - `frontend/src/api/ai.js`（新增上传与识别方法）

## 配置与安全
- 将提供的 `token` 与账号写入环境变量，代码仅从环境读取；不在仓库明文存储。

请确认以上方案，确认后我将开始实施后端与前端改造并完成端到端联调。