import streamlit as st
import subprocess
import glob
import os
import shutil
from datetime import datetime

# =========================
# AYARLAR
# =========================

st.set_page_config(
    page_title="AI Shorts Generator",
    page_icon="🎬",
    layout="wide"
)

OUTPUT_DIR = "output"
STORAGE_DIR = "storage"

os.makedirs(STORAGE_DIR, exist_ok=True)

# =========================
# CSS TASARIM
# =========================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0f1117;
        color: white;
    }

    .main-title {
        text-align: center;
        font-size: 60px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .subtitle {
        text-align: center;
        font-size: 22px;
        color: #9ca3af;
        margin-bottom: 40px;
    }

    .section-title {
        font-size: 30px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HEADER
# =========================

st.markdown(
    '<div class="main-title">🎬 AI Shorts Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI ile saniyeler içinde viral Shorts üret 😄🔥</div>',
    unsafe_allow_html=True
)

st.divider()

# =========================
# VIDEO OLUŞTUR
# =========================

st.markdown(
    '<div class="section-title">🎯 Yeni Video Oluştur</div>',
    unsafe_allow_html=True
)

video_topic = st.text_input(
    "Video konusu",
    placeholder="Örn: İnsanlar AI ile nasıl para kazanıyor"
)

if st.button(
    "🚀 Video Oluştur",
    use_container_width=True
):

    if not video_topic:

        st.warning("Konu gir 😄")

    else:

        with st.spinner("Video oluşturuluyor..."):

            process = subprocess.run(
                ["python", "main.py"],
                input=video_topic,
                text=True,
                capture_output=True
            )

            st.text(process.stdout)

            if process.stderr:
            st.error(process.stderr)

            video_files = glob.glob(
                f"{OUTPUT_DIR}/*.mp4"
            )

            if video_files:

                latest_video = max(
                    video_files,
                    key=os.path.getctime
                )

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                saved_video = os.path.join(
                    STORAGE_DIR,
                    f"video_{timestamp}.mp4"
                )

                shutil.copy(
                    latest_video,
                    saved_video
                )

                st.success("Video hazır 😄🔥")

                st.video(saved_video)

                with open(saved_video, "rb") as file:

                    st.download_button(
                        label="⬇️ Videoyu İndir",
                        data=file,
                        file_name=os.path.basename(saved_video),
                        mime="video/mp4",
                        use_container_width=True
                    )

            else:

                st.error("Video oluşturulamadı")

st.divider()

# =========================
# VIDEO GEÇMİŞİ
# =========================

st.markdown(
    '<div class="section-title">📁 Oluşturulan Videolar</div>',
    unsafe_allow_html=True
)

saved_videos = sorted(
    glob.glob(f"{STORAGE_DIR}/*.mp4"),
    key=os.path.getctime,
    reverse=True
)

if not saved_videos:

    st.info("Henüz video oluşturulmadı 😄")

else:

    for video in saved_videos:

        with st.container(border=True):

            st.video(video)

            col1, col2 = st.columns([4, 1])

            with col1:

                st.text(
                    os.path.basename(video)
                )

            with col2:

                with open(video, "rb") as file:

                    st.download_button(
                        label="İndir",
                        data=file,
                        file_name=os.path.basename(video),
                        mime="video/mp4",
                        key=video
                    )