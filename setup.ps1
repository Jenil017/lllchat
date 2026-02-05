# Setup script for FastAPI Chat Backend
# Run this script to set up your development environment

Write-Host "🚀 FastAPI Chat Backend Setup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "✓ Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[2-9]") {
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python 3.12+ required. Current: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Check if .env exists
Write-Host "✓ Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "  ! .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  ⚠ Please update .env with your database and Redis credentials" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "✓ Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "✓ Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "  ✓ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup complete! Next steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Update .env with your credentials:" -ForegroundColor White
Write-Host "   - DATABASE_URL (PostgreSQL connection string)" -ForegroundColor Gray
Write-Host "   - REDIS_URL (Redis connection string)" -ForegroundColor Gray
Write-Host "   - JWT_SECRET (generate with: openssl rand -hex 32)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Create PostgreSQL database:" -ForegroundColor White
Write-Host "   createdb chatdb" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run database migrations:" -ForegroundColor White
Write-Host "   alembic upgrade head" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start the server:" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Visit API docs:" -ForegroundColor White
Write-Host "   http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
