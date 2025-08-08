#!/bin/bash

# TAIFA-FIALA Production Deployment Script
echo "🚀 Deploying TAIFA-FIALA to production..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Sync latest changes from local to production
echo "📤 Syncing local changes to production..."
rsync -avz -e "ssh -o Ciphers=aes256-gcm@openssh.com" --exclude='.git' --exclude='node_modules' --exclude='venv' --exclude='.next' --exclude='logs' --exclude='*.log' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env.local' "$SCRIPT_DIR/" jforrest@100.75.201.24:production/TAIFA-FIALA/


# Copy .env files to production
echo "📄 Copying .env files..."
# Copy frontend production environment file
scp -o Ciphers=aes256-gcm@openssh.com "$SCRIPT_DIR/frontend/.env.production" jforrest@100.75.201.24:production/TAIFA-FIALA/frontend/.env.production
# Note: Backend .env should be managed directly on production server to avoid overwriting production secrets

# Deploy and restart services on production
echo "🔄 Restarting services on production..."
ssh -T -o Ciphers=aes256-gcm@openssh.com jforrest@100.75.201.24 << 'EOF'
cd production/TAIFA-FIALA

# Set up pyenv environment
export PATH="$HOME/.pyenv/shims:$PATH"

# Set up Node.js/nvm environment
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# Use specific Node.js version or fallback to available version
nvm use v20.19.0 2>/dev/null || nvm use node || echo "⚠️ nvm not available, using system node"
# Add npm to PATH explicitly
export PATH="$HOME/.nvm/versions/node/v20.19.0/bin:$PATH"

# Check and kill processes on ports 8030 and 3030
echo "🔍 Checking for processes on ports 8030 and 3030..."

# Function to kill process on a specific port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "⚠️ Found process on port $port (PID: $pid), killing it..."
        kill -9 $pid || true
        sleep 2
        # Verify it's gone
        local check_pid=$(lsof -ti:$port)
        if [ ! -z "$check_pid" ]; then
            echo "❌ Failed to kill process on port $port"
        else
            echo "✅ Successfully killed process on port $port"
        fi
    else
        echo "✅ Port $port is free"
    fi
}

# Kill processes on required ports
kill_port 8030
kill_port 3030

# Stop existing services (fallback) 
echo "🧹 Cleaning up old processes..."
pkill -f "uvicorn\|npm.*start\|next.*start" || true

# Clean up any remaining backend processes
pkill -f "python.*uvicorn\|python.*main.py" || true
pkill -f "start_backend.sh" || true

# Clean up old npm/pnpm processes that might be lingering
pkill -f "npm.*start" || true
pkill -f "pnpm.*start" || true

# Clean up old Python multiprocessing.resource_tracker processes (if safe)
echo "🔍 Checking for old Python resource tracker processes..."
ps aux | grep "multiprocessing.resource_tracker" | grep -v grep | awk '{print $2}' | head -5 | xargs -r kill -9 2>/dev/null || true

sleep 5

echo "✅ Process cleanup complete"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
python3 -m pip install -r requirements.txt
cd ..

# Install frontend dependencies and build
echo "📦 Installing frontend dependencies and building..."
cd frontend
npm install
# Clean build to ensure latest changes are included
rm -rf .next node_modules/.cache
# Set NODE_ENV to production for build to use .env.production
export NODE_ENV=production
npm run build
cd ..

# Create logs directory
mkdir -p logs

# Start backend with environment variables
echo "🚀 Starting backend service..."
cd backend


# Export environment variables safely
set -a  # automatically export all variables
source .env
export ENVIRONMENT=production
set +a  # stop automatically exporting

# Debug: verify key environment variables are loaded
echo "🔍 Environment variables check:"
echo "SUPABASE_URL: ${SUPABASE_URL:0:30}..." 
echo "SUPABASE_PROJECT_URL: ${SUPABASE_PROJECT_URL:0:30}..." 
echo "ENVIRONMENT: $ENVIRONMENT"

# Start backend using uvicorn on port 8030
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8030 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
cd ..

# Start frontend on port 3030
echo "🚀 Starting frontend service..."
cd frontend
# Ensure NODE_ENV is set for runtime
export NODE_ENV=production
nohup npm start -- -p 3030 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
cd ..

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Check health
echo "🔍 Checking service health..."
echo "Backend process check:"
ps aux | grep "python.*main\|uvicorn" | grep -v grep || echo "❌ No backend process found"

echo "Port 8030 check:"
lsof -i :8030 && echo "✅ Port 8030 is listening" || echo "❌ Port 8030 not listening"

echo "Testing backend endpoints:"
curl -f http://localhost:8030/health && echo "✅ Backend health OK" || echo "❌ Backend health FAILED"
# Note: Backend root endpoint returns 404 by design (no root route defined)
echo "ℹ️ Backend root endpoint returns 404 by design - this is expected"

echo "Frontend process check:"
ps aux | grep "npm.*start\|next.*start" | grep -v grep || echo "❌ No frontend process found"

echo "Port 3030 check:"
lsof -i :3030 && echo "✅ Port 3030 is listening" || echo "❌ Port 3030 not listening"

echo "Testing frontend:"
curl -f http://localhost:3030 && echo "✅ Frontend OK" || echo "❌ Frontend FAILED"

echo "📋 Service Summary:"
echo "- Backend: http://localhost:8030"
echo "- Frontend: http://localhost:3030"
echo "- Logs: ~/production/TAIFA-FIALA/logs/"

echo "✅ Deployment complete!"
EOF

echo "🌐 Check your site: https://taifa-fiala.net"
echo "📊 Backend API: https://api.taifa-fiala.net"