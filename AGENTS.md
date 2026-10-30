# Человек без лица

Проект «Человек без лица» основан на шаблоне RETRO. История и озвучка уже подготовлены пользователем. Использовать готовые материалы; не переписывать историю и не менять голос без запроса. Старые отраслевые, языковые и стилистические требования шаблона требуют адаптации и не определяют новый проект. Настройка проекта сама по себе не запускает производство.

Основной процесс: готовый текст + готовая запись → проверка соответствия и таймкоды → план сцен → материалы → согласованное звуковое оформление → монтаж → проверка. Язык и длительность определяются предоставленными материалами.

## Required skills

Before performing a requested stage, identify and read its local SKILL.md and the materials it requires for that stage. Follow its requirements during production and verification. Do not skip an applicable skill, substitute a recollection of it, or replace it with a simplified personal process. The user's latest explicit instruction takes precedence. If a required skill or resource is unavailable, report the blocker and continue independent parts of the request; do not declare the dependent stage complete.

A full episode requires the skills for every requested stage. A targeted edit requires the affected stage's skill and corresponding verification; reading every skill for every task is unnecessary.

| Stage | Skill |
|---|---|
| Full episode / continuation | [retro-engineering-produce](.agents/skills/retro-engineering-produce/SKILL.md) |
| Script | [retro-engineering-script](.agents/skills/retro-engineering-script/SKILL.md) |
| Assets | [retro-engineering-assets](.agents/skills/retro-engineering-assets/SKILL.md) |
| Sound | [retro-engineering-sound](.agents/skills/retro-engineering-sound/SKILL.md) |
| Editing | [retro-engineering-edit](.agents/skills/retro-engineering-edit/SKILL.md) |
| Metadata | [retro-engineering-metadata](.agents/skills/retro-engineering-metadata/SKILL.md) |
| Thumbnails | [retro-engineering-thumbnails](.agents/skills/retro-engineering-thumbnails/SKILL.md) |
| Shorts | [retro-engineering-shorts](.agents/skills/retro-engineering-shorts/SKILL.md) |
| Verification and cleanup | [retro-engineering-check](.agents/skills/retro-engineering-check/SKILL.md) |

## Settings and working boundaries

Precedence: latest user instruction → episode scope and settings_overrides → [settings.json](settings.json). Replace language arrays in full. For an existing episode, `inspect` returns effective_settings; `resolve` without inspect does not apply episode restrictions.

Working files belong in `Производство/episodes/`; only finished deliverables belong in `Результаты/`. Reusable assets, sources, and usage terms belong in `Данные проекта/`; tools belong in `Производство/`.

Музыка и SFX не включены в текущий запрос. При отдельном заказе видео согласовать звуковое оформление; исходная речь сохраняется отдельно. Установки и исторические разрешения старого шаблона не являются разрешением нового пользователя.

Perform only the requested scope. Project configuration does not start an episode or paid requests; Shorts require a separate request or scope.shorts. Publishing, sending materials to people, and subagents require user authorization. Make routine decisions within the request independently.

“Continue” refers to the latest request in this conversation. Check state, actual files, and the script hash; preserve the supplied narration and checked timing data. Script changes make dependent results stale. Do not change frozen parts; new thumbnails and instruction updates do not unfreeze video.

## Delivery and retention

Verify requested results using the verification skill. Export only final files through the local delivery.py with SHA-256 verification; user-facing deliverable links must point to Результаты. Export does not establish editorial readiness, and unavailable checks must not be reported as passed.

Keep inputs and recovery data until completion. After verifying finals, retain finished deliverables, assets selected for future production, and compact production.json, delivery_manifest.json, source records, and quality_report.md. Remove unnecessary episode inputs, old versions, and duplicates; do not clean the shared library along with the episode. Do not automatically restore deliverables deleted by the user. After deleting inputs, explicitly record that reproduction is unavailable; preserve verification status and limitations.

## Комплектность шаблона

В архиве отсутствуют Производство/scripts/, медиаматериалы и Данные проекта/research/. Не считать команды и проверки из старых навыков выполненными или доступными. Перед производством проверить зависимости. Подробности — ANALYSIS.md.
