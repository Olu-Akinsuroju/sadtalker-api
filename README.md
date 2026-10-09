# SadTalker API

A minimal HTTP API wrapper around [SadTalker](https://github.com/OpenTalker/SadTalker) that accepts a face image and an audio file and returns a talking-head video.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| POST | `/generate` | Generate talking-head video |

### POST /generate

**Headers**
```
X-API-Key: <your API key>
```

**Body** — `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `image` | file | Source face image (jpg / png) |
| `audio` | file | Driving audio (wav / mp3) |

**Response** — `video/mp4` file download

**Example with curl**
```bash
curl -X POST http://localhost:8000/generate \
  -H "X-API-Key: your-secret-key" \
  -F "image=@face.jpg" \
  -F "audio=@speech.wav" \
  --output result.mp4
```

## Running with Docker

```bash
docker build -t sadtalker-api .

docker run -p 8000:8000 \
  -e API_KEY=your-secret-key \
  --gpus all \
  sadtalker-api
```

> **No GPU?** Drop the `--gpus all` flag — it will run on CPU (much slower).

## Development (no Docker)

Requires a working SadTalker install at `/app/SadTalker`.

```bash
pip install -r requirements.txt
API_KEY=dev uvicorn server:app --reload
```

Interactive docs available at `http://localhost:8000/docs`.
