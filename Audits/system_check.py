import sys
import os
import socket

# 1. Check Python version
REQUIRED_MAJOR = 3
REQUIRED_MINOR = 8

def check_python_version():
    current = sys.version_info
    if current.major != REQUIRED_MAJOR or current.minor < REQUIRED_MINOR:
        print(f"❌ Python {REQUIRED_MAJOR}.{REQUIRED_MINOR}+ is required. You have {current.major}.{current.minor}.{current.micro}")
        return False
    print(f"✅ Python version is {current.major}.{current.minor}.{current.micro}")
    return True

# 2. Verify internet connection to GitHub
def check_github_connection():
    try:
        host = 'github.com'
        port = 443
        socket.setdefaulttimeout(5)
        with socket.create_connection((host, port), timeout=5):
            print("✅ Able to connect to GitHub")
            return True
    except Exception as e:
        print(f"❌ Cannot connect to GitHub: {e}")
        return False

# 3. Confirm NEnterprise folders exist
def check_nenterprise_folders():
    folders = ["audits", "patents", "saas_engine", "vc_intelligence"]
    all_exist = True
    for folder in folders:
        if not os.path.isdir(folder):
            print(f"❌ Folder missing: {folder}")
            all_exist = False
        else:
            print(f"✅ Folder exists: {folder}")
    return all_exist

if __name__ == "__main__":
    pv = check_python_version()
    git_conn = check_github_connection()
    folders = check_nenterprise_folders()
    if pv and git_conn and folders:
        print("🔎 All system checks passed!")
    else:
        print("⚠️ Some system checks failed.")
