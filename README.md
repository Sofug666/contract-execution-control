# Контроль исполнения договоров

Программа ведёт реестр договоров и показывает, какие обязательства просрочены. Сроки и ответственные указываются отдельно для каждого обязательства.

Нужен Python 3.10 или новее.

## Пример

Из папки проекта выполните в PowerShell:

```powershell
python -X utf8 contracts.py --file example.json add-contract D-01 "Учебный поставщик"
python -X utf8 contracts.py --file example.json add-obligation D-01 O-01 "Передача отчёта" "Куратор" 2026-11-20
python -X utf8 contracts.py --file example.json report --as-of 2026-11-21
python -X utf8 contracts.py --file example.json close D-01 O-01
python -X utf8 contracts.py --file example.json report --as-of 2026-11-21
```

Первый отчёт покажет «Просрочено», второй – «Выполнено». Пример рассчитан на первый запуск, когда файла `example.json` ещё нет. Без параметра `--file` программа использует `contracts.json`.

Тесты запускаются командой `python -m unittest -v`. Описание требований и структуры реестра находится в папке `docs`.
