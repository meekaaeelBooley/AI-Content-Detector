# Create python virtual environment for the packages
python -m venv venv
.\venv\Scripts\Activate.ps1

# Reason for installing from powershell: Significantly faster than installing python packages on wsl.

# Installs Python packages. Hang in tight, this will take a while. Lightweight packages are installed as we are only using the model here, not training it. Training takes place on google colab with access to stronger gpu's.
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers flask flask-cors PyPDF2 python-docx werkzeug

# Please hang on tight, this will take some time to download :)
Write-Host "Run: .\venv\Scripts\Activate.ps1 then python run.py" -ForegroundColor Green