# Формат episode.json — версия 1

## Проект

```json
{
  "version": 1,
  "brand": "НАЗВА ПРОЄКТУ",
  "title": "Название выпуска для организации проекта",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "audio": "audio/voice.wav",
  "audio_policy": "strict",
  "footer": "Название серии · период",
  "theme": {"blue": "#28608C", "yellow": "#D6AD43"},
  "scenes": []
}
```

`audio` можно убрать или поставить `null`. `theme` целиком необязателен.
Доступные поля темы: background, ink, muted, blue, yellow, olive, grid, panel,
dark, font, font_bold. Цвета — значения Pillow, например HEX. Шрифты — TTF/OTF.
Относительный путь к шрифту сначала ищется рядом с JSON, затем в корне студии.

## Общие поля сцены

- `id`: уникальное имя.
- `type`: тип шаблона.
- `duration`: положительная длительность в секундах.
- `start`: необязательное начало, для проверки непрерывности таймлайна.
- `title`: заголовок.
- `source`: строка источника внизу; заменяет footer проекта в этой сцене.

Заголовки и подписи переносятся и уменьшаются внутри своей области. Если даже
минимальный размер не позволяет вместить текст, превью/рендер завершается ошибкой.
Не превращайте карточки в абзацы: короткие подписи читаются лучше.

## intro / section / outro

Центральный заголовок: `eyebrow`, `title`, `subtitle`.

```json
{"id":"intro","type":"intro","duration":4,"eyebrow":"СЕРІЯ","title":"Тема випуску","subtitle":"Коротке питання"}
```

## item

Предмет слева, название и факты справа. Максимум 3 факта.

```json
{"id":"bag","type":"item","duration":7,"category":"СПОРЯДЖЕННЯ","image":"assets/bag.png","title":"Наплічник","subtitle":"Короткий опис","facts":["Факт 1","Факт 2"],"note":"Обмеження або пояснення","source":"Джерело: ..."}
```

## compare

Ровно 2 элемента в `sides`. Каждый: label, title, image, detail.

```json
{"id":"comparison","type":"compare","duration":6,"title":"Порівняння","sides":[{"label":"А","title":"Перший варіант","image":"assets/a.png","detail":"Коротка відмінність"},{"label":"Б","title":"Другий варіант","image":"assets/b.png","detail":"Коротка відмінність"}]}
```

## bars

От 1 до 6 горизонтальных столбцов. Только неотрицательные значения. `maximum`
не должен быть меньше наибольшего значения. `display` — форматированная подпись.
`unit` обозначает единицы измерения. Цвет: имя из theme либо HEX.

```json
{"id":"chart","type":"bars","duration":5,"title":"Умовний приклад","unit":"умовні одиниці","maximum":10,"values":[{"label":"А","value":8,"display":"8","color":"blue"},{"label":"Б","value":5,"display":"5","color":"olive"}],"note":"Демонстраційні дані"}
```

## kit

От 1 до 6 предметов. Каждый: image, label. Сетка подбирается по количеству.

```json
{"id":"kit","type":"kit","duration":6,"title":"Комплект","items":[{"image":"assets/a.png","label":"Предмет А"},{"image":"assets/b.png","label":"Предмет Б"}]}
```

## diagram

От 2 до 4 блоков со стрелками. Каждый: title, detail. Вся сцена может иметь note.

```json
{"id":"logic","type":"diagram","duration":6,"title":"Логіка пояснення","nodes":[{"title":"Питання","detail":"Що з’ясовуємо"},{"title":"Порівняння","detail":"Що бачимо"},{"title":"Висновок","detail":"Що це означає"}]}
```

## footage

`video` — путь, `in` — начальная секунда, `loop` — зациклить, `fit` — cover или
contain. При loop после конца файл повторяется с начала. Звук вставки не используется.
Без loop длительность сцены не должна выходить за конец исходника.

```json
{"id":"clip","type":"footage","duration":5,"video":"assets/clip.mp4","in":2,"loop":false,"fit":"cover","title":"Пояснення до кадрів","subtitle":"Короткий контекст","source":"Джерело відео: ..."}
```

### Готовые архивные подписи

Для `footage` поле `"baked_captions": true` означает, что флаг, название и источник
уже вмонтированы в исходный видеоклип. Предпросмотр и обычный рендер не добавляют
повторную большую плашку. `render-fast` сохраняет подготовленные подписи.

`tools/prepare_archive.py EPISODE --library DIRECTORY` готовит фрагменты по
`archive_edit: {source, in, country}`; источники описываются в JSON, указанном в
`archive_sources`. Это рецепт монтажного проекта, а не восстановление видео по
фотографии. `external_media_manifest` задаёт манифест готовых вставок для
`tools/fetch_episode_media.py`; размер и SHA-256 каждого файла проверяются.
