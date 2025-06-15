import os
import requests

def download_font():
    folder = "utils"
    if not os.path.exists(folder):
        os.makedirs(folder)
    font_path = os.path.join(folder, "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(font_path, "wb") as f:
                f.write(r.content)
            print("تم تحميل الخط بنجاح وحفظه في:", font_path)
        except Exception as e:
            print(f"فشل تحميل الخط: {e}")
    else:
        print("الخط موجود مسبقًا:", font_path)

if __name__ == "__main__":
    download_font()

