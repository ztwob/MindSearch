# RAG and Multimodal Extension Plan

This project can now be run with the existing MindSearch `/solve` endpoint plus
three extension endpoints that make RAG and multimodal integration testable
without requiring a new vector database or vision model on day one.

## Local run path

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the API with a low-friction search backend:

   ```bash
   python -m mindsearch.app --lang cn --model_format gpt4 --search_engine DuckDuckGoSearch
   ```

   Set `OPENAI_API_KEY` when using `gpt4`. For the original InternLM server
   mode, start the LMDeploy service first and keep `--model_format
   internlm_server`.

3. Exercise RAG endpoints:

   ```bash
   curl -X POST http://127.0.0.1:8002/rag/index \
     -H 'Content-Type: application/json' \
     -d '{"documents":[{"id":"intro","text":"MindSearch builds a graph of search subquestions."}]}'

   curl -X POST http://127.0.0.1:8002/rag/search \
     -H 'Content-Type: application/json' \
     -d '{"query":"graph search", "top_k":3}'
   ```

4. Exercise the multimodal normalization endpoint:

   ```bash
   curl -X POST http://127.0.0.1:8002/multimodal/normalize \
     -H 'Content-Type: application/json' \
     -d '{"inputs":[{"type":"text","text":"Describe this"},{"type":"image_url","image_url":{"url":"https://example.com/a.png"}}]}'
   ```

## Architecture

- `mindsearch.rag` contains an `InMemoryRAGStore` with a BM25-like lexical
  scorer. It is process-local and intended as the stable interface for later
  FAISS, Milvus, Elasticsearch, or pgvector backends.
- `mindsearch.multimodal` normalizes string, OpenAI-style text parts, image
  URLs, and base64 image payloads into a small internal schema.
- `mindsearch.app` exposes `/rag/index`, `/rag/search`, and
  `/multimodal/normalize` independently from `/solve`, so the existing agent
  flow remains unchanged while new clients can be developed and tested.

## Next production steps

1. Replace `InMemoryRAGStore` with a persistent vector backend and an embedding
   service.
2. Inject retrieved snippets into `GenerationParams.agent_cfg` or the searcher
   prompt before calling `init_agent`.
3. Route normalized image parts to a vision-capable LLM or OCR/image-captioning
   tool and merge the resulting text into the planner context.
