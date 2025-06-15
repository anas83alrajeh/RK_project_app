import requests
import os

def download_font():
    url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "DejaVuSans.ttf")

    try:
        print(f"Downloading font from {url} ...")
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"Font downloaded and saved to {save_path}")
    except Exception as e:
        print(f"Failed to download font: {e}")

if __name__ == "__main__":
    download_font()
