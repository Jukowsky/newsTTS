#!/bin/bash

# Turkish News TTS Application Runner Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.7 or higher."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Found Python $python_version"
}

# Check if required packages are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    # Try to import required packages
    python3 -c "import requests, bs4, openai, schedule" 2>/dev/null
    if [ $? -ne 0 ]; then
        print_warning "Some dependencies are missing. Installing..."
        pip3 install -r requirements.txt
        if [ $? -ne 0 ]; then
            print_error "Failed to install dependencies!"
            exit 1
        fi
    fi
    
    print_status "Dependencies OK"
}

# Check if OpenAI API key is set
check_api_key() {
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY environment variable is not set."
        echo "Please set it using: export OPENAI_API_KEY='your-api-key-here'"
        echo "Or modify the script to include your API key directly."
        
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_status "OpenAI API key is set"
    fi
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    
    mkdir -p audio_files
    mkdir -p logs
    
    print_status "Directories created"
}

# Main execution function
run_app() {
    local app_file="news_tts_app_enhanced.py"
    
    if [ ! -f "$app_file" ]; then
        app_file="news_tts_app.py"
        if [ ! -f "$app_file" ]; then
            print_error "Application file not found!"
            exit 1
        fi
    fi
    
    print_status "Starting Turkish News TTS Application..."
    print_status "Using: $app_file"
    print_status "Press Ctrl+C to stop"
    echo
    
    python3 "$app_file"
}

# Show usage information
show_usage() {
    echo "Turkish News TTS Application Runner"
    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  run, start    Start the application (default)"
    echo "  check         Check dependencies and configuration"
    echo "  demo          Run TTS demo only"
    echo "  docker        Run using Docker"
    echo "  help          Show this help message"
    echo
    echo "Environment Variables:"
    echo "  OPENAI_API_KEY    Your OpenAI API key (required)"
    echo
    echo "Examples:"
    echo "  $0                # Start the application"
    echo "  $0 check          # Check setup"
    echo "  $0 demo           # Run demo"
    echo "  OPENAI_API_KEY='sk-...' $0 run"
}

# Run demo only
run_demo() {
    print_status "Running TTS demo..."
    python3 -c "
from news_tts_app_enhanced import NewsTTSApp
app = NewsTTSApp()
result = app.demo_turkish_tts()
if result:
    print('Demo completed successfully!')
    print(f'Audio file: {result}')
else:
    print('Demo failed!')
"
}

# Run with Docker
run_docker() {
    print_status "Running with Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    if [ ! -f "docker/docker-compose.yml" ]; then
        print_error "Docker configuration not found!"
        exit 1
    fi
    
    cd docker
    docker-compose up --build
}

# Check setup
check_setup() {
    print_status "Checking setup..."
    check_python
    check_dependencies
    check_api_key
    setup_directories
    print_status "Setup check completed!"
}

# Main script logic
case "${1:-run}" in
    "run"|"start"|"")
        check_python
        check_dependencies
        check_api_key
        setup_directories
        run_app
        ;;
    "check")
        check_setup
        ;;
    "demo")
        check_python
        check_dependencies
        check_api_key
        run_demo
        ;;
    "docker")
        run_docker
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac

