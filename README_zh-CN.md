<div id="top"></div>

<div align="center">

<img src="assets/logo.svg" style="width: 50%; height: auto;">

[📃 Paper](https://arxiv.org/abs/2407.20183) | [💻 浦语入口](https://internlm-chat.intern-ai.org.cn/)

[English](README.md) | 简体中文

<https://github.com/user-attachments/assets/b4312e9c-5b40-43e5-8c69-929c373e4965>

</div>
</p>

## ✨ MindSearch: Mimicking Human Minds Elicits Deep AI Searcher

MindSearch 是一个开源的 AI 搜索引擎框架，具有与 Perplexity.ai Pro 相同的性能。您可以轻松部署它来构建您自己的搜索引擎，可以使用闭源 LLM（如 GPT、Claude）或开源 LLM（[InternLM2.5 系列模型](https://huggingface.co/internlm/internlm2_5-7b-chat)经过专门优化，能够在 MindSearch 框架中提供卓越的性能；其他开源模型没做过具体测试）。其拥有以下特性：

- 🤔 **任何想知道的问题**：MindSearch 通过搜索解决你在生活中遇到的各种问题
- 📚 **深度知识探索**：MindSearch 通过数百网页的浏览，提供更广泛、深层次的答案
- 🔍 **透明的解决方案路径**：MindSearch 提供了思考路径、搜索关键词等完整的内容，提高回复的可信度和可用性。
- 💻 **多种用户界面**：为用户提供各种接口，包括 React、Gradio、Streamlit 和本地调试。根据需要选择任意类型。
- 🧠 **动态图构建过程**：MindSearch 将用户查询分解为图中的子问题节点，并根据 WebSearcher 的搜索结果逐步扩展图。

<div align="center">

<img src="assets/teaser.gif">

</div>

## ⚡️ MindSearch VS 其他 AI 搜索引擎

在深度、广度和生成响应的准确性三个方面，对 ChatGPT-Web、Perplexity.ai（Pro）和 MindSearch 的表现进行比较。评估结果基于 100 个由人类专家精心设计的现实问题，并由 5 位专家进行评分\*。

<div align="center">
<img src="assets/mindsearch_openset.png" width="90%">
</div>
* 所有实验均在 2024 年 7 月 7 日之前完成。

## ⚽️ 构建您自己的 MindSearch

### 步骤1: 依赖安装

建议使用 Python 3.10 或 3.11 创建独立环境后再安装依赖。Windows 上如果使用
Python 3.13，部分依赖可能没有预编译 wheel，`pip` 会尝试下载 Rust
工具链并停在 `Preparing metadata (pyproject.toml)` / `downloading 6 components`
较久。遇到这种情况优先切换到 Python 3.10 环境，而不是继续等待源码编译。

```bash
# conda 推荐方式
conda create -n mindsearch python=3.10 -y
conda activate mindsearch
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

如果在 Windows PowerShell 中执行 `py -3.10 -m venv .venv` 时提示
`No suitable Python runtime found`，说明本机尚未安装 Python 3.10。请先安装
Miniconda/Anaconda，或者从 Python 官网/Microsoft Store/winget 安装 Python
3.10，然后重新打开终端再创建虚拟环境。安装后可用以下命令确认系统识别到了
Python 3.10：

```powershell
py -0p
py -3.10 --version
```

如果 Windows 安装依赖时报 `Failed to build func-timeout timeout-decorator`，并且
包含 `[WinError 3] The system cannot find the path specified: 'd:\\'`，通常是
PowerShell 的临时目录或缓存目录指向了不存在的 D 盘。请把 `TEMP`、`TMP` 和
`PIP_CACHE_DIR` 指到存在的目录后重试：

```powershell
New-Item -ItemType Directory -Force $env:LOCALAPPDATA\Temp | Out-Null
New-Item -ItemType Directory -Force $env:LOCALAPPDATA\pip\Cache | Out-Null
$env:TEMP = "$env:LOCALAPPDATA\Temp"
$env:TMP = "$env:LOCALAPPDATA\Temp"
$env:PIP_CACHE_DIR = "$env:LOCALAPPDATA\pip\Cache"
python -m pip cache purge
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
```

如果只是在已有环境中安装：

```bash
pip install -r requirements.txt
```

完成 `python -m compileall mindsearch` 后，可继续参考 [Windows 本地跑通流程](./docs/windows_runbook_zh.md)
按顺序验证后端、RAG、多模态归一化和 `/solve` 接口。

### 步骤2: 启动 MindSearch API

启动 FastAPI 服务器

```bash
python -m mindsearch.app --lang en --model_format internlm_server --search_engine DuckDuckGoSearch
```

- `--lang`: 模型的语言，`en` 为英语，`cn` 为中文。
- `--model_format`: 模型的格式。
  - `internlm_server` 为 InternLM2.5-7b-chat 本地服务器。
  - `gpt4` 为 GPT4。
    如果您想使用其他模型，请修改 [models](./mindsearch/agent/models.py)
- `--search_engine`: 搜索引擎。
  - `DuckDuckGoSearch` 为 DuckDuckGo 搜索引擎。
  - `BingSearch` 为 Bing 搜索引擎。
  - `BraveSearch` 为 Brave 搜索引擎。
  - `GoogleSearch` 为 Google Serper 搜索引擎。
  - `TencentSearch` 为 Tencent 搜索引擎。
    
  请将 DuckDuckGo 和 Tencent 以外的网页搜索引擎 API 密钥设置为 `WEB_SEARCH_API_KEY` 环境变量。如果使用 DuckDuckGo，则无需设置；如果使用 Tencent，请设置 `TENCENT_SEARCH_SECRET_ID` 和 `TENCENT_SEARCH_SECRET_KEY`。
 
### 步骤3: 启动 MindSearch 前端

提供以下几种前端界面：

- React

首先配置Vite的API代理，指定实际后端URL

```bash
HOST="127.0.0.1"
PORT=8002
sed -i -r "s/target:\s*\"\"/target: \"${HOST}:${PORT}\"/" frontend/React/vite.config.ts
```

```bash
# 安装 Node.js 和 npm
# 对于 Ubuntu
sudo apt install nodejs npm
# 对于 Windows
# 从 https://nodejs.org/zh-cn/download/prebuilt-installer 下载

cd frontend/React
npm install
npm start
```

更多细节请参考 [React](./frontend/React/README.md)

- Gradio

```bash
python frontend/mindsearch_gradio.py
```

- Streamlit

```bash
streamlit run frontend/mindsearch_streamlit.py
```

## 🐞 本地调试

```bash
python mindsearch/terminal.py
```

## 📝 许可证

该项目按照 [Apache 2.0 许可证](LICENSE) 发行。

## 学术引用

如果此项目对您的研究有帮助，请参考如下方式进行引用：

```
@article{chen2024mindsearch,
  title={MindSearch: Mimicking Human Minds Elicits Deep AI Searcher},
  author={Chen, Zehui and Liu, Kuikun and Wang, Qiuchen and Liu, Jiangning and Zhang, Wenwei and Chen, Kai and Zhao, Feng},
  journal={arXiv preprint arXiv:2407.20183},
  year={2024}
}
```

## 相关项目

关注我们其他在大语言模型上的一些探索，主要为LLM智能体方向。

- [Lagent](https://github.com/InternLM/lagent): 一个轻便简洁的大语言模型智能体框架
- [AgentFLAN](https://github.com/InternLM/Agent-FLAN): 一套构建高质量智能体语料和训练模型的方法 (ACL 2024 Findings)
- [T-Eval](https://github.com/open-compass/T-Eval): 一个细粒度评估LLM调用工具能力的评测及 (ACL 2024)
