# CE Demo - CrewAI Enterprise Demo Application

A comprehensive enterprise application demonstrating the integration of CrewAI with FastAPI, Kubernetes, and modern DevOps practices.

## Project Structure

```
ce-demo/
├── src/                    # Main source code
│   ├── api/               # FastAPI application
│   ├── crews/             # CrewAI crews and agents
│   ├── models/            # Data models and schemas
│   ├── utils/             # Utility functions
│   └── database/          # Database configuration and models
├── tests/                 # Test files
├── k8s/                   # Kubernetes manifests
├── helm/                  # Helm charts
├── scripts/               # Utility scripts
├── frontend/              # Next.js application
├── docker/                # Dockerfiles
└── .github/workflows/     # GitHub Actions CI/CD
```

## Features

- **FastAPI Backend**: High-performance async API
- **CrewAI Integration**: AI-powered autonomous agents
- **Kubernetes Ready**: Fully containerized with K8s manifests
- **Helm Charts**: Easy deployment and configuration
- **Next.js Frontend**: Modern React-based UI
- **CI/CD Pipeline**: Automated testing and deployment

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- Kubernetes cluster (for deployment)
- Helm 3+

## Getting Started

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run the application:
   ```bash
   uvicorn src.api.main:app --reload
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

## Testing

Run tests with pytest:
```bash
pytest
```

With coverage:
```bash
pytest --cov=src tests/
```

## Docker

Build the Docker image:
```bash
docker build -f docker/Dockerfile -t ce-demo:latest .
```

## Deployment

### Kubernetes

Apply Kubernetes manifests:
```bash
kubectl apply -f k8s/
```

### Helm

Install using Helm:
```bash
helm install ce-demo helm/ce-demo
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.