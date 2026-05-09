import os
import time
import random
import asyncio
import textwrap
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from moviepy import (
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
    ImageClip,
    CompositeVideoClip
)

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

OUTPUT_DIR = "output"
ASSETS_DIR = "assets"
TEXT_DIR = "text_assets"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920


SCRIPTS = {
    "ai": {
        "hook": "BU AI HER ŞEYİ DEĞİŞTİREBİLİR",
        "text": (
            "Bu yapay zekâ araçları internette inanılmaz hızla yayılmaya başladı. "
            "İnsanlar artık saniyeler içinde video oluşturabiliyor, görseller hazırlayabiliyor "
            "ve hatta kod yazabiliyor. Eskiden saatler süren işler artık birkaç dakika içinde "
            "tamamlanıyor. Bazı insanlar bu araçlarla internetten para kazanmaya başladı bile. "
            "Özellikle içerik üreticileri ve girişimciler yapay zekâyı kullanarak işlerini büyütüyor. "
            "Teknolojinin bu kadar hızlı gelişmesi birçok kişiyi hem heyecanlandırıyor hem de korkutuyor."
        ),
        "keywords": [
            "artificial intelligence",
            "computer technology",
            "future technology",
            "social media",
            "business laptop",
            "digital creator"
        ]
    },

    "para": {
        "hook": "İNSANLAR BUNUNLA PARA KAZANIYOR",
        "text": (
            "İnternetten para kazanmak artık eskisi kadar zor değil. "
            "İnsanlar kısa videolar, dijital ürünler ve yapay zekâ araçlarıyla gelir üretmeye başladı. "
            "Özellikle sosyal medya sayesinde milyonlarca kişiye ulaşmak artık çok daha kolay hale geldi. "
            "Bazı içerik üreticileri sadece telefon kullanarak ciddi gelirler elde ediyor. "
            "Buradaki en önemli nokta mükemmel olmak değil, düzenli içerik üretmek ve doğru sistemi kurmak."
        ),
        "keywords": [
            "money",
            "business",
            "success",
            "phone creator",
            "laptop business",
            "social media"
        ]
    },

    "gizem": {
        "hook": "İNTERNETİN KARANLIK TARAFI",
        "text": (
            "İnternette bazı siteler var ki çoğu insan bunların varlığını bilmiyor. "
            "Bazıları eski arşivleri gösteriyor, bazıları dünyanın farklı noktalarındaki canlı kameraları açıyor. "
            "Teknoloji ilerledikçe gerçek ile sahteyi ayırmak çok daha zor hale geliyor. "
            "Artık sesler kopyalanabiliyor, videolar değiştirilebiliyor ve yapay zekâ gerçek olmayan görüntüler oluşturabiliyor."
        ),
        "keywords": [
            "mystery internet",
            "dark technology",
            "computer screen",
            "cyber",
            "internet",
            "technology"
        ]
    },

    "futbol": {
        "hook": "FUTBOL TARİHİNE GEÇEN AN",
        "text": (
            "Futbol tarihindeki bazı anlar hâlâ milyonlarca insan tarafından unutulmuyor. "
            "Özellikle son dakika golleri ve inanılmaz geri dönüş maçları futbolun neden bu kadar sevildiğini gösteriyor. "
            "Büyük stadyum atmosferleri, taraftar sesleri ve kritik anlarda gelen goller bu sporu efsane yapıyor. "
            "Bazı futbolcular sadece yetenekleriyle değil, çalışma disiplinleriyle de tarihe geçti."
        ),
        "keywords": [
            "football stadium",
            "soccer match",
            "football fans",
            "goal celebration",
            "stadium lights",
            "football training"
        ]
    }
}


def clean_folder(folder):
    for file in os.listdir(folder):
        try:
            os.remove(os.path.join(folder, file))
        except:
            pass


def clean_assets():
    clean_folder(ASSETS_DIR)
    clean_folder(TEXT_DIR)


def choose_content(topic):
    t = topic.lower()

    if "para" in t or "kazan" in t or "gelir" in t:
        selected = SCRIPTS["para"]
    elif "gizem" in t or "site" in t or "korku" in t:
        selected = SCRIPTS["gizem"]
    elif "futbol" in t or "ronaldo" in t or "messi" in t or "gol" in t:
        selected = SCRIPTS["futbol"]
    else:
        selected = SCRIPTS["ai"]

    return selected["hook"], selected["text"], selected["keywords"]


async def generate_voice(text):
    import edge_tts

    audio_path = os.path.join(OUTPUT_DIR, "voice.mp3")

    communicate = edge_tts.Communicate(
        text,
        "tr-TR-AhmetNeural"
    )

    await communicate.save(audio_path)

    return audio_path


def download_scene_videos(keywords):
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    paths = []

    for keyword in keywords:
        url = (
            "https://api.pexels.com/videos/search"
            f"?query={keyword}"
            "&per_page=8"
            "&orientation=portrait"
        )

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            continue

        videos = response.json().get("videos", [])
        random.shuffle(videos)

        for video in videos:
            files = video.get("video_files", [])

            if not files:
                continue

            best_file = sorted(
                files,
                key=lambda x: x.get("width", 0),
                reverse=True
            )[0]

            video_url = best_file["link"]
            video_data = requests.get(video_url).content

            path = os.path.join(
                ASSETS_DIR,
                f"{int(time.time())}_{len(paths)}.mp4"
            )

            with open(path, "wb") as f:
                f.write(video_data)

            paths.append(path)
            break

    return paths


def make_text_image(text, filename, font_size=64, y_padding=40):
    img = Image.new("RGBA", (WIDTH, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text.upper(), width=24)

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=font,
        spacing=10,
        stroke_width=4
    )

    text_w = bbox[2] - bbox[0]
    x = (WIDTH - text_w) / 2

    draw.multiline_text(
        (x, y_padding),
        wrapped,
        font=font,
        fill="white",
        stroke_fill="black",
        stroke_width=5,
        align="center",
        spacing=10
    )

    path = os.path.join(TEXT_DIR, filename)
    img.save(path)

    return path


def split_sentences(text):
    parts = []

    for sentence in text.replace("\n", " ").split("."):
        sentence = sentence.strip()
        if sentence:
            parts.append(sentence + ".")

    return parts


def create_caption_clips(script, total_duration):
    sentences = split_sentences(script)

    if not sentences:
        return []

    duration_each = total_duration / len(sentences)
    clips = []

    for i, sentence in enumerate(sentences):
        img_path = make_text_image(
            sentence,
            f"caption_{i}.png",
            font_size=54
        )

        clip = (
            ImageClip(img_path)
            .with_start(i * duration_each)
            .with_duration(duration_each)
            .with_position(("center", 1380))
        )

        clips.append(clip)

    return clips


def fit_video_clip(clip):
    clip = clip.resized(height=HEIGHT)

    if clip.w < WIDTH:
        clip = clip.resized(width=WIDTH)

    x_center = clip.w / 2
    y_center = clip.h / 2

    clip = clip.cropped(
        width=WIDTH,
        height=HEIGHT,
        x_center=x_center,
        y_center=y_center
    )

    return clip


def create_video(video_paths, audio_path, hook, script):
    if not video_paths:
        raise Exception("Pexels video bulunamadı.")

    audio = AudioFileClip(audio_path)
    target_duration = audio.duration

    duration_per_clip = target_duration / len(video_paths)

    clips = []

    for path in video_paths:
        try:
            clip = VideoFileClip(path)

            clip_duration = min(duration_per_clip, clip.duration)

            clip = (
                clip
                .subclipped(0, clip_duration)
            )

            clip = fit_video_clip(clip)

            clips.append(clip)

        except Exception as e:
            print("Clip atlandı:", e)

    if not clips:
        raise Exception("Hiç kullanılabilir video yok.")

    base_video = concatenate_videoclips(
        clips,
        method="compose"
    )

    while base_video.duration < target_duration:
        base_video = concatenate_videoclips(
            [base_video, base_video],
            method="compose"
        )

    base_video = base_video.subclipped(0, target_duration)

    hook_img = make_text_image(
        hook,
        "hook.png",
        font_size=76
    )

    hook_clip = (
        ImageClip(hook_img)
        .with_start(0)
        .with_duration(min(4, target_duration))
        .with_position(("center", 180))
    )

    caption_clips = create_caption_clips(
        script,
        target_duration
    )

    final_video = CompositeVideoClip(
        [base_video, hook_clip] + caption_clips,
        size=(WIDTH, HEIGHT)
    )

    final_video = final_video.with_audio(audio)

    output_path = os.path.join(
        OUTPUT_DIR,
        f"video_{int(time.time())}.mp4"
    )

    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )

    audio.close()
    base_video.close()
    final_video.close()

    for clip in clips:
        clip.close()

    return output_path


def main():
    clean_assets()

    topic = input().strip()

    print("İçerik hazırlanıyor...")
    hook, script, keywords = choose_content(topic)

    print("Ses oluşturuluyor...")
    audio_path = asyncio.run(generate_voice(script))

    print("Sahne videoları indiriliyor...")
    video_paths = download_scene_videos(keywords)

    print("Video renderlanıyor...")
    final_video = create_video(
        video_paths,
        audio_path,
        hook,
        script
    )

    print("\nBİTTİ")
    print(final_video)


if __name__ == "__main__":
    main()