# 🚀 OpenAI Status Monitor

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)<br>
</br>
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com/)<br>
</br>
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)<br>
</br>
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<br>
</br>
> **Production-ready FastAPI application** that automatically tracks and logs service updates from status pages like OpenAI's Status Page. Built with enterprise-grade features including webhook processing, intelligent polling, and horizontal scaling capabilities.
<br>
</br>
## 🎯 **Problem Statement Solved**
<br>
</br>
<br>
</br>
**Challenge**: Build a Python script that automatically tracks OpenAI service updates without manual polling inefficiency, scalable to 100+ status pages.<br>
</br>

**Solution**: Event-driven architecture with webhook-first approach + intelligent ETag-based polling fallback.<br>
</br>

**Output**: Real-time console notifications in the exact format required:<br>
</br>
```
[2025-11-18 12:34:56] Product: OpenAI API - Chat Completions
Status: Investigating degraded performance
```

---

---
<br>
</br>
A production-ready FastAPI application that automatically tracks and logs service updates from status pages like OpenAI's Status Page. Supports both webhook-based event delivery and efficient polling with smart caching.
<br>
</br>
## 🏗️ **Architecture Overview**
<br>
</br>
<br>
</br>
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Status Pages  │───▶│  FastAPI Server  │───▶│  Console Output │
│  (OpenAI, etc.) │    │  - Webhooks      │    │  [Formatted]    │
└─────────────────┘    │  - Polling       │    └─────────────────┘
                       │  - Deduplication │           │
┌─────────────────┐    │  - Health Checks │    ┌─────────────────┐
│     Redis       │◀───┤                  │    │   Structured    │
│  (Optional)     │    └──────────────────┘    │    Logging      │
└─────────────────┘                            └─────────────────┘
```
<br>
</br>
## 🚀 **Key Technical Features**<br>
</br>
<br>
</br>
- **🔄 Event-Driven**: Webhook-first architecture with polling fallback<br>
</br>
- **⚡ Performance**: ETag/If-Modified-Since HTTP caching<br>
</br>
- **🔒 Security**: HMAC-SHA256 signature verification<br>
</br>
- **📊 Monitoring**: Health checks, structured logging, metrics<br>
</br>
- **🌐 Scalability**: Redis clustering, horizontal scaling ready<br>
</br>
- **🧪 Testing**: Comprehensive test suite with multiple scenarios<br>
</br>
- **🐳 DevOps**: Docker support with docker-compose<br>
</br>

## 🎯 Assignment Requirements Met
<br>
</br><br>
</br>
✅ **Event-driven approach**: Primary webhook endpoint (`/webhook`) for real-time updates  <br>
</br>
✅ **Efficient polling fallback**: Uses ETag/If-Modified-Since to minimize data transfer   <br>
</br>
✅ **Scalable architecture**: Redis deduplication, structured logging, health checks   <br>
</br>
✅ **Console output**: Prints formatted status updates as required   <br>
</br>
✅ **Deduplication**: Prevents duplicate status updates across restarts <br>
</br>

## ✨ Features
 <br>
</br> <br>
</br>
### Core Functionality 
- **FastAPI webhook endpoint** (`/webhook`) to receive incident and component updates <br>
</br>
- **Efficient poller** for status summary endpoints (uses ETag/If-Modified-Since caching) <br>
</br>
- **Smart deduplication** (in-memory by default, Redis for persistence across restarts) <br>
</br>
- **HMAC signature verification** for webhook security (supports both plain hex and `sha256=` formats) <br>
</br>
- **Component ID mapping** for readable product names in console output <br>
</br>
- **Health check endpoint** (`/health`) for monitoring and service discovery <br>
</br>

### Production Improvements <br>
</br> <br>
</br>
- **Structured logging** with configurable log levels (replaces print statements) <br>
</br>
- **Graceful error handling** with automatic Redis fallback <br>
</br>
- **TTL-based cleanup** for deduplication sets to prevent memory leaks <br>
</br>
- **Robust signature verification** supporting multiple webhook formats <br>
</br>
- **Background task management** for long-running poller processes <br>
</br>

## 📋 Requirements
 <br>
</br> <br>
</br>
- Python 3.11+ <br>
</br>
- Dependencies: `fastapi`, `uvicorn[standard]`, `httpx`, `python-dateutil`, `redis>=4.5.0`
 <br>
</br>
## 🚀 Quick Start
 <br>
</br> <br>
</br>
### Option 1: Local Development
```bash
# 1. Clone repository
git clone https://github.com/saumyamalviya00/OpenAI-status-Monitor.git
cd OpenAI-status-Monitor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env as needed

# 4. Run application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Test (in new terminal)
python test_webhook.py
```

### Option 2: Docker
```bash
# Run with Docker Compose (includes Redis)
docker-compose up -d

# Or standalone Docker
docker build -t status-monitor .
docker run -p 8000:8000 status-monitor
```

### 🎬 **Live Demo**

Once running, test with this webhook payload:
```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "id": "demo_001",
      "name": "OpenAI API - Chat Completions",
      "incident_updates": [{
        "id": "upd_001", 
        "created_at": "2025-11-18T12:34:56Z",
        "body": "Investigating degraded performance"
      }]
    }
  }'
```

**Console Output:**
```
[2025-11-18 12:34:56] Product: OpenAI API - Chat Completions
Status: Investigating degraded performance
```

## 🔧 Configuration

Create a `.env` file with these options:

```bash
# HMAC secret for webhook verification (optional)
SIGNING_SECRET=your_webhook_secret_here

# Redis URL for persistent deduplication (optional)
REDIS_URL=redis://localhost:6379/0

# Enable/disable polling fallback
ENABLE_POLLER=1

# Status page to monitor
STATUS_SUMMARY_URL=https://status.openai.com/api/v2/summary.json

# Polling interval in seconds
POLL_INTERVAL_SECONDS=30

# Logging level
LOG_LEVEL=INFO
```

## 🧪 Testing

### Test Webhook with Sample Payload

```powershell
$body = '{
  "incident": {
    "id": "inc_001",
    "name": "OpenAI API - Chat Completions", 
    "incident_updates": [
      {
        "id": "upd_001",
        "created_at": "2025-11-18T12:34:56Z",
        "body": "Investigating degraded performance"
      }
    ]
  }
}'

curl -X POST "http://127.0.0.1:8000/webhook" -H "Content-Type: application/json" -d $body
```

**Expected Console Output:**
```
[2025-11-18 12:34:56] Product: OpenAI API - Chat Completions
Status: Investigating degraded performance
```

### Test Health Endpoint

```powershell
curl http://localhost:8000/health
```

### Run Comprehensive Tests

```powershell
python test_webhook.py
```

## 📊 API Endpoints

- **`POST /webhook`** - Receive webhook events from status providers
- **`GET /health`** - Health check and service status

## 🏗️ Scaling to 100+ Status Pages

For production deployment monitoring hundreds of status pages:

### Architecture Recommendations

1. **Webhook-First Approach**
   - Configure webhook endpoints with each status provider
   - Use load balancer (ALB/nginx) to distribute webhook traffic
   - Deploy multiple app instances behind the load balancer

2. **Message Queue Integration**
   - Route webhooks → SQS/SNS → Lambda/ECS workers
   - Decouple ingestion from processing for better fault tolerance
   - Enable parallel processing of multiple status updates

3. **Shared Storage**
   - Use managed Redis cluster (ElastiCache/MemoryDB) for deduplication
   - Set TTL policies to prevent unbounded growth
   - Consider sharding by provider for very high scale

4. **Monitoring & Observability**
   - Structured logging → CloudWatch/ELK/Datadog
   - Health checks for service discovery (ECS/K8s)
   - Metrics for webhook success/failure rates

### Example Serverless Architecture

```
Status Providers → API Gateway → Lambda → SQS → Lambda Workers → Redis
                                   ↓
                               CloudWatch Logs
```

## 🔒 Security

- **HMAC Verification**: Supports both `X-Signature: hex` and `X-Signature: sha256=hex` formats
- **Input Validation**: Handles malformed JSON and unexpected payload structures  
- **Rate Limiting**: Consider adding rate limiting for production deployments
- **TLS**: Always use HTTPS in production environments

## 🐳 Docker Support

```bash
# Build and run with Docker
docker build -t status-monitor .
docker run -p 8000:8000 status-monitor

# Or use Docker Compose with Redis
docker-compose up
```

## 📝 Logs and Monitoring

The application now uses structured logging:

```json
{
  "timestamp": "2025-11-18 12:34:56",
  "level": "INFO",
  "logger": "app.main",
  "message": "Status update",
  "extra": {
    "product": "OpenAI API - Chat Completions",
    "status": "Investigating degraded performance", 
    "incident_id": "inc_001",
    "update_id": "upd_001"
  }
}
```

## 🤝 Contributing

This implementation fulfills the assignment requirements with production-ready enhancements:
- Event-driven webhook processing ✅
- Efficient polling with caching ✅  
- Scalable deduplication strategy ✅
- Console output as specified ✅
- Ready for 100+ provider monitoring ✅

## 📈 **Performance & Scaling**

- **Webhook Processing**: Sub-millisecond response times
- **Memory Efficient**: TTL-based cleanup prevents memory leaks  
- **Redis Clustering**: Horizontal scaling for deduplication
- **Background Tasks**: Non-blocking poller with exponential backoff
- **Load Balancer Ready**: Health checks for service discovery

## 🛠️ **Tech Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI + Uvicorn | High-performance async web server |
| **HTTP Client** | httpx | Async HTTP requests with connection pooling |
| **Caching** | Redis | Persistent deduplication across restarts |
| **Logging** | Python logging | Structured logs for monitoring |
| **Testing** | pytest + requests | Comprehensive test coverage |
| **Deployment** | Docker + Compose | Containerized deployment |

## 🤝 **Contributing**

This project demonstrates production-ready Python development practices:

1. **Code Quality**: Type hints, error handling, documentation
2. **Testing**: Unit tests, integration tests, manual test scripts  
3. **Security**: HMAC verification, input validation
4. **Observability**: Health checks, structured logging
5. **DevOps**: Docker, environment configuration, scaling guides

Feel free to fork and extend for your own status monitoring needs!

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built for a technical assignment demonstrating event-driven architecture and scalable system design. Ready for production deployment.**
#   O p e n A I - s t a t u s - M o n i t o r 
 

 

