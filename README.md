# EALogger

EALogger is a lightweight Python logging utility.

## Installation Process

Follow these steps to set up and install EALogger:

### 1. Install FastAPI
If you haven't already, install FastAPI and Uvicorn:


### 2. Clone this repository
Clone the repository to your local machine:
    https://github.com/hasanmasudnet/eaLogger.git

### 3. Install EALogger
Navigate to the cloned directory and install the wheel:

pip install --upgrade {directory}\eaLogger\eaLogger-0.1.6-py3-none-any.whl

pip install --upgrade eaLogger\eaLogger-0.1.6-py3-none-any.whl

### 4. Verify Installation
Open a Python shell and test:

from EALogger import set_default_app_name, get_logger, log_entry_exit

set_default_app_name("EALogger")

logger = get_logger(__name__, username="")

### 5. Rename the package
Set-ExecutionPolicy -Scope Process Bypass -Force
RenamePythonPackage.ps1 -PackageDir "D:\Python\log02\EALogger" -OldName "alanlogger" -NewName "EALogger"
