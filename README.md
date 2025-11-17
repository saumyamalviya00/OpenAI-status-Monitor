# 🚀 OpenAI Status Monitor
 <br>
</br>
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
</br> <br>
</br>
## 🎯 **Problem Statement Solved**
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
</br> <br>
</br>
## 🏗️ **Architecture Overview**
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
</br> <br>
</br>
## 🚀 **Key Technical Features**<br>
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
 <br>
</br>
## 🎯 Assignment Requirements Met
<br>
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
 <br></br>
## ✨ Features
 <br>
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
 <br>
</br>
### Production Improvements <br>
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
 <br>
</br>
## 📋 Requirements
 <br>
</br>
- Python 3.11+ <br>
</br>
- Dependencies: `fastapi`, `uvicorn[standard]`, `httpx`, `python-dateutil`, `redis>=4.5.0`
 <br>
</br> <br>
</br>
## 🚀 Quick Start
 <br>
</br> 
### Option 1: Local Development <br>
</br>
```bash
# 1. Clone repository <br>
</br>
git clone https://github.com/saumyamalviya00/OpenAI-status-Monitor.git <br>
</br>
cd OpenAI-status-Monitor <br>
</br>

# 2. Install dependencies <br>
</br>
pip install -r requirements.txt <br>
</br>

# 3. Configure environment <br>
</br>
cp .env.example .env <br>
</br>
# Edit .env as needed <br>
</br>

# 4. Run application <br>
</br>
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
 <br>
</br>
# 5. Test (in new terminal) <br>
</br>
python test_webhook.py <br>
</br>
```

### Option 2: Docker <br>
</br>
```bash 
# Run with Docker Compose (includes Redis) <br>
</br>
docker-compose up -d <br>
</br>

# Or standalone Docker <br>
</br>
docker build -t status-monitor . <br>
</br>
docker run -p 8000:8000 status-monitor <br>
</br>
```
 <br>
</br>

## 📊 API Endpoints <br>
</br>

- **`POST /webhook`** - Receive webhook events from status providers <br>
</br>
- **`GET /health`** - Health check and service status <br>
</br>

## 🏗️ Scaling to 100+ Status Pages <br>
</br>

For production deployment monitoring hundreds of status pages: <br>
</br>
 <br>
</br>
### Architecture Recommendations <br>
</br>

1. **Webhook-First Approach** <br>
</br>
   - Configure webhook endpoints with each status provider <br></br>
   - Use load balancer (ALB/nginx) to distribute webhook traffic<br></br>
   - Deploy multiple app instances behind the load balancer<br></br>

2. **Message Queue Integration** <br>
</br>
   - Route webhooks → SQS/SNS → Lambda/ECS workers<br></br>
   - Decouple ingestion from processing for better fault tolerance<br></br>
   - Enable parallel processing of multiple status updates<br></br>
 <br>
</br>
3. **Shared Storage** <br>
</br>
   - Use managed Redis cluster (ElastiCache/MemoryDB) for deduplication<br></br>
   - Set TTL policies to prevent unbounded growth<br></br>
   - Consider sharding by provider for very high scale<br></br>
 <br>
</br>
4. **Monitoring & Observability** <br>
</br>
   - Structured logging → CloudWatch/ELK/Datadog<br></br>
   - Health checks for service discovery (ECS/K8s)<br></br>
   - Metrics for webhook success/failure rates<br></br>
 <br>
</br>
### Example Serverless Architecture
 <br>
</br>
```
Status Providers → API Gateway → Lambda → SQS → Lambda Workers → Redis
                                   ↓
                               CloudWatch Logs
```
 <br>
</br>
## 🔒 Security
 <br>
</br>
- **HMAC Verification**: Supports both `X-Signature: hex` and `X-Signature: sha256=hex` formats<br></br>
- **Input Validation**: Handles malformed JSON and unexpected payload structures  <br></br>
- **Rate Limiting**: Consider adding rate limiting for production deployments<br></br>
- **TLS**: Always use HTTPS in production environments<br></br>
 <br>
</br>
