# Космос — конец Вселенной, V2

[Открыть сборку в Google Colab](https://colab.research.google.com/github/anzelina878-collab/v1/blob/cosmos-universum-v2/cosmos/001-universum-v2/Render_Colab.ipynb)

138 планов, 26:00, 1920×1080, 25 fps. Стоковые кадры, архивы и объёмные научные визуализации; без плоских схем, нумерованных полос и постоянных технических подписей. Оригинальная немецкая озвучка сохраняется.

## Облачная сборка

Открыть ноутбук, подключить свой Google Drive, загрузить исходный `l966a-enchz (1).mp3`, выполнить ячейки. Результат записывается в `MyDrive/Cosmos/001-universum-v2/Universum_V2_1080p.mp4`. Доступ к вашему Colab/Drive не создаётся фактом размещения ноутбука на GitHub; требуется ваша Google-сессия.

## Локально

Python 3.10+ и FFmpeg с libx264/libfreetype.

```bash
python download_project_assets.py --project .
python render.py --project . --audio voiceover.mp3 --output Universum_V2_1080p.mp4
```

Исходник озвучки не загружен в публичный GitHub. Файлы скачиваются с официальных страниц, адреса и полные credits находятся в plan.json и SOURCES.md. Архивы низшего исходного разрешения не объявляются нативным Full HD.

Активный редакторский навык находится в `../.agents/skills/cinematic-space/SKILL.md`; SKILL.md в папке выпуска — его копия. Старые проекты и шаблоны других каналов не менялись.
