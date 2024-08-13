# Пример CI/CD пайплайна для Java приложения

## Стек

+ docker compose + dockerfile для образов
+ приложение [OpenTest](https://github.com/mcdcorp/opentest) (распространяется под лицензией [MIT](https://github.com/mcdcorp/opentest?tab=MIT-1-ov-file))

## В работе

+ создать пайплайн для Jenkins
+ создать пайплайн для GitLab

## Описание

+ приложение состоит из двух контейнеров - WebUI-сервера и исполнителя, который подключается к серверу
+ после запуска WebUI доступен на порту 3000
+ образы сделаны на основе [node:20-alpine](https://hub.docker.com/_/node) для уменьшения итогового размера; как альтернатива рассматривался [ibmjava](https://hub.docker.com/_/ibmjava)
+ в качестве тестового репозитория взят пример из официального [быстрого старта](https://getopentest.org/docs/installation.html#quick-start) (data)
