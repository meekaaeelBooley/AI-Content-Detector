# Run Redis inside WSL and then start the python flask app

# Start Redis in WSL (requires sudo password ). Neat trick to run commands in wsl from powershell.
wsl -e bash -c "sudo systemctl start redis-server"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run python application
python run.py
