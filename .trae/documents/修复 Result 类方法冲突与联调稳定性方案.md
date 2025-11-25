**问题诊断**

* AttributeError: success 源于 `Result` 模型中字段名与类方法同名（`success`、`error`），在 Pydantic v2 下类属性被字段定义占用，导致类方法访问冲突。
* Illegal header value b'Bearer ' 来源于 LLM/Embedding 请求头未携带有效密钥；需确保 `settings.llm_api_key` 在进程启动时读取到环境变量。
* All connection attempts failed 多为 Redis API 未运行引起，已容错；但需抑制噪声日志并避免影响主流程。
* 404 /@vite/client 属正常（前端资源不应由后端提供）。

**修复方案**

1) `Result` 类重命名类方法以避免与字段同名冲突
* 将类方法：
  * `Result.success(...)` → `Result.ok(...)`
  * `Result.error(...)` → `Result.fail(...)`
  * `Result.error_with_code(...)` → `Result.fail_with_code(...)`
* 同步替换全局使用位置：
  * `python/app/api/v1/ai.py`（返回对话结果）
  * `python/app/main.py`（异常处理器）
  * （如有）其他模块对 `Result` 的调用

2) LLM 密钥加载与校验
* 确认 `Settings` 可从环境变量 `LLM_API_KEY` 读取（字段 `llm_api_key`）；重启时打印一条启动日志显示是否为空（仅调试）。
* 若为空，后退读取 `DASHSCOPE_API_KEY`，并在初始化时赋值到 `settings.llm_api_key`。

3) Redis 未启动的容错与日志
* 维持当前容错（返回空上下文），但将 `BaseHTTPClient.get/post` 的错误日志级别调降为 `warning`，避免噪声；或在 RedisClient 内部捕获并返回空值。

**代码改动点**
* `python/app/common/response.py`：重命名类方法并保留返回结构；不改字段与序列化（`model_dump`）。
* `python/app/api/v1/ai.py`：`Result.ok(...)` 替换原 `Result.success(...)`；
* `python/app/main.py`：`Result.fail(...)`/`Result.fail_with_code(...)` 替换原错误返回；保留 `model_dump()`。
* 可选：在 `app/main.py` 启动生命周期中打印 `settings.llm_api_key` 是否存在（不输出具体值，仅布尔）。

**验证步骤**
* 重启后端，执行：
  * 前端提问 → 后端日志应为 `200 OK`，不再有 `AttributeError: success`。
  * 若 Redis 未运行，仅出现 `warning`，接口仍返回有效 `reply.content` 与 `reply.sources`。
* 前端页面展示回答与引用来源；网络面板无 401/500。

**注意**
* 不打印真实密钥；仅检查是否为空。
* 保持现有响应结构与字段名不变（`success`、`message`、`data`、`error`、`timestamp`）。