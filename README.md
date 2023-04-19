[![Coverage Status](https://coveralls.io/repos/github/woowgers/radium_assessment_task/badge.svg?branch=main)](https://coveralls.io/github/woowgers/radium_assessment_task?branch=main)

# Тестовое задание по вакансии "Python Backend Developer" компании "Radium"
## Требования задания:
- Напишите скрипт, асинхронно, в 3 одновременных задачи, скачивающий содержимое HEAD репозитория https://gitea.radium.group/radium/project-configuration во временную папку.
- После выполнения всех асинхронных задач скрипт должен посчитать sha256 хэши от каждого файла.
- Код должен проходить без замечаний проверку линтером wemake-python-styleguide. Конфигурация nitpick - https://gitea.radium.group/radium/project-configuration
- Обязательно 100% покрытие тестами

## Использованные источники:
- [nitpick docs](https://nitpick.readthedocs.io/en/latest/index.html)
- [repository api](https://gitea.radium.group/api/swagger#/repository)
