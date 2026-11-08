# АРСЕНАЛ 360° — випуск 007

Франція проти Великої Британії. Оригінальна українська озвучка: 14:59.448. Відео: Full HD, 30 кадрів/с, 14:59.467.

Власний світлий стиль серії: повільні 3D-оберти, перевірені фото техніки, документальні відео, 3D-рельєф Європи, заставки розділів і запитання глядачеві. Фото нерухомі, інформаційні плашки з’являються один раз. Сценарій та аудіо не змінені.

## Відтворення з архіву

У ZIP є готові медіа й вихідна геометрія. Після розпакування:

```bash
cd video-studio
python -m venv .venv
.venv/bin/pip install -r episodes/007-france-uk/requirements-visual.txt
cd episodes/007-france-uk
../../.venv/bin/python build_episode.py
../../.venv/bin/python render_episode.py --preview --work /tmp/arsenal007-preview
../../.venv/bin/python render_episode.py --work /tmp/arsenal007-render --output output/final_video_v1.mp4
../../.venv/bin/python verify_episode.py output/final_video_v1.mp4 --compiled /tmp/arsenal007-render --output output/qa
```

Потрібні Python 3.10+ і FFmpeg/FFprobe у PATH. Для перебудови геометричних банків потрібен numba, для нового відділення фону — rembg/onnxruntime та модель ISNet; для звичайної збірки вони не потрібні. Пакет вимог підготовки окремий.

Сценарна розмітка — visual_map.py, правила монтажу — build_episode.py, обрані діапазони архівів — source-windows.json. Для нового тексту потрібно заново зіставити смислові сцени з озвучкою; автоматично підставляти випадкові матеріали не слід. Існуючі випуски не змінюються.

Джерела й умови використання — SOURCES.md та assets/manifest.json. Перевірки — output/qa. Суцільний людський перегляд із прослуховуванням не проводився; автоматичний повний декод і покадрові контрольні перевірки описані окремо.
