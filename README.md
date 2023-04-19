[![Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/woowgers/868d6a62a68d261d8e26d2d20808090d/raw/radium_assessment_task__heads_main.json)]

# Тестовое задание по вакансии "Python Backend Developer" компании "Radium"
## Требования задания:
- Напишите скрипт, асинхронно, в 3 одновременных задачи, скачивающий содержимое HEAD репозитория https://gitea.radium.group/radium/project-configuration во временную папку.
- После выполнения всех асинхронных задач скрипт должен посчитать sha256 хэши от каждого файла.
- Код должен проходить без замечаний проверку линтером wemake-python-styleguide. Конфигурация nitpick - https://gitea.radium.group/radium/project-configuration
- Обязательно 100% покрытие тестами

## Использованные источники:
- [nitpick docs](https://nitpick.readthedocs.io/en/latest/index.html)
- [repository api](https://gitea.radium.group/api/swagger#/repository)
