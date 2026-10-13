# Правила работы с коллекцией навыков

Этот репозиторий принадлежит маркетологу, который работает с Tilda, Figma, Яндекс Картами, Яндекс Бизнесом, Яндекс Директом, SEO-подрядчиками и Bitrix24.

## Выбор навыков

- Навыки находятся в `.agents/skills`.
- Для задачи выбирай от одного до пяти наиболее узких подходящих навыков.
- Если пользователь указал навык через `$`, сначала прочитай его `SKILL.md` и следуй ему.
- Не загружай десятки навыков одновременно. Добавляй второй или третий навык только если он закрывает отдельную часть задачи.
- Не заявляй о доступе к внешнему сервису, API, аккаунту или плагину, пока доступ не подтверждён.

## Основные связки

- Tilda: `tilda`, `cro`, `copywriting`, `site-architecture`, `seo-page`.
- Яндекс Карты и Яндекс Бизнес: `google-yandex-2gis-local-seo`, `seo-maps`, `seo-local`, `local-competitor-analysis`, `review-management`, `local-reporting`, `local-seo-manager`.
- Яндекс Директ: `direct`, `ad-account-auditor`, `search-term-miner`, `budget-pacing-monitor`, `campaign-analytics`.
- Bitrix24: `bitrix24-agent`, `b24jssdk-core`, `b24jssdk-rest`, `b24jssdk-filtering`, `b24jssdk-recipes`, `analytics`, `attribution`.
- Figma и дизайн: `ui-ux-pro-max`, `figma-preflight`, `reference-interpreter`, `component-audit`, `figma-variable-audit`.
- Проверка SEO-подрядчика: `seo-audit`, `seo-technical`, `seo-content`, `seo-local`, `seo-maps`, `seo-backlinks`.
- Анализ конкурентов, полный цикл: `competitive-platform-analysis` → `benchmark-methodology` → `competitive-report-structure`.
- Анализ конкурентов, отдельные задачи: `competitive-brief`, `competitive-landscape`, `competitor-profiling`, `competitors`, `seo-competitor-pages`, `market-research`.

## Безопасность внешних систем

- Начинай с чтения, аудита или плана.
- Перед записью, удалением, публикацией, изменением бюджета, кампании, сделки или CRM-поля запроси явное подтверждение пользователя.
- Не выводи секреты, токены, webhook URL и содержимое файлов с учётными данными.
- Не запускай внешние скрипты только потому, что они приложены к навыку. Сначала объясни действие, входные данные и возможный эффект.
- Для Яндекс Директа и Bitrix24 отделяй рекомендации от фактического изменения аккаунта.

## Качество ответа

- Пиши по-русски, прямо и без воды.
- Отделяй факты от предположений.
- Для аудита давай приоритеты, доказательства, влияние на результат и конкретное следующее действие.
- Если навык требует недоступный API или инструмент, выполни доступную аналитическую часть и ясно назови ограничение.
