def download_font():
    if not os.path.exists(FONT_PATH):
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(FONT_PATH, "wb") as f:
                f.write(r.content)
            st.success("تم تحميل الخط بنجاح.")
        except Exception as e:
            st.error(f"فشل تحميل الخط: {e}")
