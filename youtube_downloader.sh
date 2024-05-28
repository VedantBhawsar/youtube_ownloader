#!/bin/bash

# Function to check for script updates
check_updates() {
    # Fetch the latest version information from GitHub API
    latest_version=$(curl -s https://api.github.com/repos/yourusername/youtube_downloader/releases/latest | grep tag_name | cut -d '"' -f 4)
    
    # Compare the latest version with the current version
    if [ "$latest_version" != "v1.0" ]; then
        echo "A new version of the script is available. Please update."
        exit 1
    fi
}

# Function for logging
setup_logging() {
    # Create a logs directory if it doesn't exist
    mkdir -p logs
    
    # Generate a log file name with timestamp
    log_file="logs/event_$(date +'%Y-%m-%d_%H-%M-%S').log"
    
    # Redirect all output (stdout and stderr) to the log file
    exec &> >(tee -a "$log_file")
}

# Function to set up the virtual environment
setup_virtualenv() {
    # Check if the virtual environment directory exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    else
        echo "Virtual environment already exists. Skipping creation."
    fi
    
    # Activate the virtual environment
    source venv/bin/activate
}

# Function to install required Python packages
install_dependencies() {
    # Check if pip3 is installed
    if ! command -v pip3 &> /dev/null; then
        echo "Error: pip3 is not installed. Please install Python 3 and pip3."
        exit 1
    fi
    
    # Check if requirements.txt file exists
    if [ ! -f requirements.txt ]; then
        echo "Error: requirements.txt file not found."
        exit 1
    fi
    
    # List of required Python packages
    required_packages=("pytube" "tqdm" "curses")
    
    # Check if required packages are installed and install them if necessary
    packages_not_installed=()
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            packages_not_installed+=("$package")
        fi
    done
    
    if [ ${#packages_not_installed[@]} -eq 0 ]; then
        echo "All required Python packages are already installed."
    else
        echo "Installing required Python packages..."
        pip3 install -r requirements.txt
    fi
}

# Function to package the application with PyInstaller
package_main() {
    # Check if the application is already packaged
    if [ ! -f "./dist/main" ]; then
        echo "Packaging the application using PyInstaller..."
        pyinstaller --onefile main.py
        
        # Check the exit status of PyInstaller
        if [ $? -eq 0 ]; then
            echo "Application packaged successfully."
        else
            echo "Error occurred during packaging. Please check the logs for details."
            exit 1
        fi
    else
        echo "Application is already packaged. Skipping packaging step."
    fi
}

# Function for downloading videos using the packaged application
download_videos() {
    # Execute the packaged application with command line arguments
    ./dist/main
}

# Main script execution starts here

# Check for script updates (optional)
# check_updates

# Set up logging
setup_logging

# Set up the virtual environment
setup_virtualenv

# Install required Python packages
install_dependencies

# Package the application
package_main

# Download videos using the packaged application
download_videos | tee /dev/tty

# Check if download was successful
if [ $? -ne 0 ]; then
    echo "An error occurred during the download process. Please check the log file for details."
    echo "Error details:"
    cat "$log_file"  # Display log file content for troubleshooting
fi
