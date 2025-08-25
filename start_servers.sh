#!/bin/bash

# ShortGPT Dual Frontend Server Starter
# Runs both FastAPI backend and React frontend

echo "🎬 Starting ShortGPT Dual Frontend System"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $FASTAPI_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Trap CTRL+C
trap cleanup SIGINT

# Check if we're in the right directory
if [ ! -f "api/main.py" ] || [ ! -d "web" ]; then
    echo -e "${RED}❌ Error: Please run this script from the ShortGPT root directory${NC}"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Error: Python virtual environment not found${NC}"
    echo "Please create venv first: python3 -m venv venv"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "web/node_modules" ]; then
    echo -e "${RED}❌ Error: Node modules not found${NC}"
    echo "Please install dependencies: cd web && npm install"
    exit 1
fi

echo -e "${BLUE}🐍 Starting FastAPI Backend...${NC}"

# Start FastAPI backend
source venv/bin/activate
python api/main.py &
FASTAPI_PID=$!

# Wait a bit for FastAPI to start
sleep 3

# Check if FastAPI started successfully
if ! kill -0 $FASTAPI_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start FastAPI backend${NC}"
    exit 1
fi

echo -e "${GREEN}✅ FastAPI Backend running on http://localhost:8000${NC}"

echo -e "${BLUE}⚛️  Starting React Frontend...${NC}"

# Start React frontend
cd web
npm run dev &
REACT_PID=$!

# Wait a bit for React to start
sleep 5

# Check if React started successfully
if ! kill -0 $REACT_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start React frontend${NC}"
    kill $FASTAPI_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ React Frontend running on http://localhost:5173${NC}"

echo ""
echo -e "${GREEN}🚀 Both servers are running!${NC}"
echo "================================="
echo -e "${BLUE}📱 React Frontend:${NC} http://localhost:5173/"
echo -e "${BLUE}🔌 FastAPI Backend:${NC} http://localhost:8000/"
echo -e "${BLUE}📖 API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "   • Asset Library: http://localhost:5173/assets"
echo "   • Config Page: http://localhost:5173/config"
echo "   • API Health: http://localhost:8000/api/health"
echo ""
echo -e "${YELLOW}⏹️  Press CTRL+C to stop both servers${NC}"

# Keep script running and monitor processes
while true; do
    # Check if FastAPI is still running
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo -e "${RED}❌ FastAPI backend stopped unexpectedly${NC}"
        kill $REACT_PID 2>/dev/null
        exit 1
    fi
    
    # Check if React is still running
    if ! kill -0 $REACT_PID 2>/dev/null; then
        echo -e "${RED}❌ React frontend stopped unexpectedly${NC}"
        kill $FASTAPI_PID 2>/dev/null
        exit 1
    fi
    
    sleep 5
done