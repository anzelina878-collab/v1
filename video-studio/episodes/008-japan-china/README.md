# Японія проти Китаю · АРСЕНАЛ 360°

Випуск 008. 1920×1080, 30 fps, 17:16.200. Незмінена авторська українська озвучка.

## Збірка з підготовлених матеріалів

Потрібні Python 3.10+, FFmpeg/ffprobe, Pillow і NumPy. Після розпакування ZIP:

```bash
cd video-studio
python -m pip install -r episodes/008-japan-china/requirements-visual.txt
cd episodes/008-japan-china
python build_episode.py
python render_episode.py --work /tmp/arsenal008-render --output /tmp/arsenal008-final.mp4
python verify_episode.py /tmp/arsenal008-final.mp4 --compiled /tmp/arsenal008-render --output output/qa
python verify_motion.py /tmp/arsenal008-render output/qa/motion.json
```

Для перегляду сцен: `python render_episode.py --preview --work /tmp/arsenal008-preview`.
Для перших 90 секунд: додайте `--pilot 90` до команди рендеру.

## Наступні випуски

Скопіюйте папку в новий номер. Покладіть незмінені сценарій та MP3 у input/ і audio/. Словесні прив'язки формує align_audio.py (додатково faster-whisper). Оновіть visual_map.py, точні словесні вставки build_episode.py, країни й прапори, assets/manifest.json та перевірені source-windows.json. Не підміняйте нову модель схожою технікою. Заново перевірте ліцензії, зміст архівів, контрольні кадри та озвучку.

Фото нерухомі. Інформаційні картки мають один вступ і зупиняються. Справжня 3D-модель F-35B обертається зі швидкістю 15°/с; коротка сцена показує частину оберту. Карти — рельєфна геометрія з плавною камерою. Невдалу геометрію OH-1 відхилено; іншу техніку показано реальними фото, а не імітацією 3D.

Усі використані матеріали, оригінали фото, вихідна модель з ліцензією, шрифти, карти, сценарій, озвучка та звіти включено. MP4 постачається окремо. Посилання, автори, ліцензії й зміни — SOURCES.md і assets/manifest.json. Ліцензії сторонніх матеріалів зберігають чинність.

Технічні перевірки не є суцільним людським переглядом і прослуховуванням. Точний обсяг контролю записано в output/qa/.
