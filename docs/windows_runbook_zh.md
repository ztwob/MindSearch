# Windows 本地跑通 MindSearch 流程

本文档面向已经完成 `python -m compileall mindsearch` 的 Windows 用户，按从后端
启动到接口验证的顺序继续跑通项目。

## 1. 确认当前环境

在项目根目录执行：

```powershell
python --version
python -m pip --version
```

建议使用 Python 3.10 或 3.11。如果此前遇到 `d:\` 临时目录问题，请先按
`README_zh-CN.md` 的 Windows 排障步骤修复 `TEMP`、`TMP` 和 `PIP_CACHE_DIR`。

## 2. 配置 DeepSeek API（可选但推荐）

DeepSeek 提供 OpenAI 兼容的 Chat Completions 接口。本项目内置 `deepseek`
模型配置，默认使用 `deepseek-v4-flash`，也可以通过环境变量改成
`deepseek-v4-pro`。

PowerShell 使用 `$env:变量名=...`：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
$env:DEEPSEEK_API_BASE="https://api.deepseek.com/chat/completions"
```

Anaconda Prompt 默认是 `cmd.exe` 语法，不能使用 `$env:`。请改用 `set`：

```bat
set DEEPSEEK_API_KEY=你的 DeepSeek API Key
set DEEPSEEK_MODEL=deepseek-v4-flash
set DEEPSEEK_API_BASE=https://api.deepseek.com/chat/completions
```

这些命令只在当前终端窗口生效。不要把真实 API Key 提交到代码仓库或公开聊天；
如果误贴了 key，请到 DeepSeek 控制台撤销并重新生成。

如果暂时没有模型 API key，也可以先跳过 `/solve`，只测试不依赖大模型的
RAG 和多模态归一化接口。

## 3. 启动 FastAPI 后端

```powershell
python -m mindsearch.app --host 127.0.0.1 --port 8002 --lang cn --model_format deepseek --search_engine DuckDuckGoSearch
```

看到 `Uvicorn running on http://127.0.0.1:8002` 后，不要关闭这个终端。
浏览器打开 `http://127.0.0.1:8002/` 可以查看 FastAPI 接口文档。

如果没有配置 DeepSeek，可以临时使用原有配置启动接口文档和 RAG/多模态接口，
但调用 `/solve` 时仍需要可用的大模型配置：

```powershell
python -m mindsearch.app --host 127.0.0.1 --port 8002 --lang cn --model_format gpt4 --search_engine DuckDuckGoSearch
```

## 4. 测试 RAG 写入和查询

新开一个 PowerShell 窗口，在项目目录执行：

```powershell
curl.exe -X POST http://127.0.0.1:8002/rag/index `
  -H "Content-Type: application/json" `
  -d '{"documents":[{"id":"doc-1","text":"MindSearch 会把用户问题拆成多个搜索子问题。"},{"id":"doc-2","text":"RAG 通常包含文档切分、召回、重排和上下文注入。"}]}'
```

预期返回：

```json
{"indexed":2}
```

然后查询：

```powershell
curl.exe -X POST http://127.0.0.1:8002/rag/search `
  -H "Content-Type: application/json" `
  -d '{"query":"RAG 包含哪些步骤？","top_k":3}'
```

预期 `results` 中能看到 `doc-2`。

## 5. 测试多模态归一化接口

```powershell
curl.exe -X POST http://127.0.0.1:8002/multimodal/normalize `
  -H "Content-Type: application/json" `
  -d '{"inputs":[{"type":"text","text":"请描述这张图片"},{"type":"image_url","image_url":{"url":"https://example.com/a.png"}}]}'
```

预期返回包含两个标准化后的 part：一个 `text`，一个 `image_url`。

## 6. 测试 MindSearch `/solve`

确认后端终端使用的是 `--model_format deepseek`，并且已经设置
`DEEPSEEK_API_KEY` 后执行：

```powershell
curl.exe -N -X POST http://127.0.0.1:8002/solve `
  -H "Content-Type: application/json" `
  -d '{"inputs":"请用中文解释 MindSearch 的工作流程。","session_id":1001}'
```

`/solve` 是流式接口，返回会分多段输出。如果报 401，请检查 API key；如果报
model not found，请检查 `DEEPSEEK_MODEL` 是否为 DeepSeek 当前支持的模型名。

## 7. 可选：启动 React 前端

保持后端运行，另开终端：

```powershell
cd frontend/React
npm install
npm start
```

如果前端代理地址为空，请按 README 中的 Vite 代理说明把后端地址配置到
`frontend/React/vite.config.ts`。

## 8. 排查 `{"detail":"Not Found"}`

如果调用 `/rag/index`、`/rag/search` 或 `/multimodal/normalize` 返回
`{"detail":"Not Found"}`，说明当前 8002 端口上的后端进程没有加载到新增路由。
常见原因是后端是在修改代码前启动的、启动目录不是当前仓库、端口上运行的是另一个
旧服务，或者本地代码尚未包含 RAG/多模态改动。

按以下顺序排查：

1. 停掉后端终端里的旧服务，通常按 `Ctrl+C`。
2. 确认当前目录是 MindSearch 仓库根目录，并且文件里存在新增路由：

   ```powershell
   python -c "from mindsearch.app import app; print([route.path for route in app.routes])"
   ```

   输出里应该包含 `/rag/index`、`/rag/search` 和 `/multimodal/normalize`。

3. 重新启动后端：

   ```powershell
   python -m mindsearch.app --host 127.0.0.1 --port 8002 --lang cn --model_format deepseek --search_engine DuckDuckGoSearch
   ```

4. 新开终端确认 OpenAPI 文档中包含 RAG 路由：

   ```powershell
   curl.exe http://127.0.0.1:8002/openapi.json | findstr /C:"/rag/index"
   ```

   如果查不到 `/rag/index`，说明你访问的仍然不是包含新增代码的后端进程。


## 9. 排查 `ModuleNotFoundError: No module named 'janus'`

`python -m compileall mindsearch` 只检查语法，不会真正导入第三方依赖。
如果执行 `from mindsearch.app import app` 或启动后端时报 `No module named 'janus'`，
说明依赖还没有完整安装到当前激活的 Python/conda 环境里。

先确认当前解释器和 pip 是同一个环境：

```powershell
python -c "import sys; print(sys.executable)"
python -m pip --version
```

然后补装缺失依赖，推荐先装完整 requirements：

```powershell
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
```

如果只是想立刻修复 `janus` 继续验证后端，可先单独安装：

```powershell
python -m pip install janus -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
```

后续如果继续出现 `ModuleNotFoundError: No module named 'xxx'`，继续用
`python -m pip install xxx` 安装到同一个环境，或者重新完整执行 requirements 安装。


## 10. 排查 `There was an error parsing the body`

如果 Windows 下 `curl.exe -d "...中文 JSON..."` 返回
`{"detail":"There was an error parsing the body"}`，通常是 `cmd.exe`/PowerShell
命令行转义或中文编码导致 JSON 请求体没有按预期发送。最稳妥的方式是把请求体写入
UTF-8 JSON 文件，再用 `--data-binary @文件名` 发送。

在项目根目录创建 `rag_index.json`：

```json
{"documents":[{"id":"doc-1","text":"MindSearch 会把用户问题拆成多个搜索子问题。"},{"id":"doc-2","text":"RAG 通常包含文档切分、召回、重排和上下文注入。"}]}
```

然后执行：

```powershell
curl.exe -X POST http://127.0.0.1:8002/rag/index -H "Content-Type: application/json; charset=utf-8" --data-binary @rag_index.json
```

同理，查询请求可以写入 `rag_search.json`：

```json
{"query":"RAG 包含哪些步骤？","top_k":3}
```

再执行：

```powershell
curl.exe -X POST http://127.0.0.1:8002/rag/search -H "Content-Type: application/json; charset=utf-8" --data-binary @rag_search.json
```

调用接口的终端可以是 `(base)` 环境，因为它只运行 `curl.exe`；真正需要安装 Python
依赖和设置模型环境变量的是运行后端服务的那个终端。
