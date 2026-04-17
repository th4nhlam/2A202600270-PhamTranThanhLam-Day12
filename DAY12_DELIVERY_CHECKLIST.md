#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** _________________________  
> **Student ID:** _________________________  
> **Date:** _________________________

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Điều gì xảy ra nếu bạn push code với API key hardcode lên GitHub public? 
Lộ API key, ảnh hưởng bảo mật
2. Tại sao stateless quan trọng khi scale? 
Giúp scale dễ dàng hơn, không phụ thuộc vào trạng thái của server
3. 12-factor nói "dev/prod parity" — nghĩa là gì trong thực tế? 
Dev và prod phải giống nhau
...

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode trong file | Biến môi trường (`env`) | Bảo mật, dễ thay đổi qua từng môi trường. |
| Logging | `print()` console | Thư viện Logging (JSON) | Chuẩn hoá cấu trúc và chống lộ metadata. |
| Server  | Chạy ở 127.0.0.1 tĩnh | Chạy ở 0.0.0.0 với port động | Cần public port để thiết lập gateway từ ngoài gọi vào. |
| Debug   | Bật Auto-reload & Traceback | Lọc lỗi và tắt Traceback công khai | Vừa tối ưu tốc độ chạy vừa tránh lộ cấu trúc stacktrace cho hacker. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11` (Bản đầy đủ, tốn dung lượng ổ đĩa)
2. Working directory: `/app`
3. Tại sao `COPY requirements.txt .` rồi `RUN pip install` TRƯỚC khi `COPY . .`?
Để tận dụng tối đa tính năng cache của Docker. Nếu không sửa gì trong dependencies thì Docker sẽ không tốn thời gian tải và cài lại Python packages mỗi khi code (`app.py`) thay đổi.
4. `.dockerignore` nên chứa gì?
Nên chứa `.env` (bảo vệ secrets), `venv/`, `__pycache__` để tiết kiệm tài nguyên bộ nhớ cho image build ra.

### Exercise 2.3: Image size comparison
- Develop: 800 MB
- Production: 130 MB
- Difference: 83.7%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://keen-gratitude-production-fa06.up.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
```bash
# Output test không API Key:
$ curl -X POST https://localhost:8000/ask -d '{"question":"Hello"}'
HTTP/1.1 403 Forbidden
{"detail": "Invalid API Key"}

# Output test hợp lệ:
$ curl -H "X-API-Key: secret-agent-key" -X POST ...
HTTP/1.1 200 OK
{"answer": "Agent is working ..."}

# Output test Rate Limiting (Quá 10 Req/phút):
HTTP/1.1 429 Too Many Requests
{"detail": "Rate limit exceeded"}
```

### Exercise 4.4: Cost guard implementation
Trong file `cost_guard.py`, em đếm độ dài câu hỏi client nhập vào qua route POST. Nếu `len(question) > 500`, hệ thống sẽ trả về lỗi `HTTP 400 Bad Request` ngay lập tức để tiết kiệm token cho LLM. Ngoài ra cấu hình thêm `max_tokens` ngắn khi gọi hàm LLM `ask(...)` để không sinh payload thừa.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
Sử dụng docker-compose để mount một Nginx server đóng vai trò Reverse Proxy (cổng port: 80/443). Phía sau cấu hình khoảng 3 replica containers ứng dụng chạy độc lập (Stateless). Khi có request từ user, ngnix chuyển tiếp load cân bằng (round-robin) xuống các container App. 
Nếu tắt ngẫu nhiên 1 App (Giả lập App crash) thì req kế tiếp vẫn xử lý thành công vì Nginx tự bypass request đó qua App còn sống. Đảm bảo mô hình luôn hoạt động (Zero Downtime).
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
