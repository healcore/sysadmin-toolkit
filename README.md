# Sysadmin Toolkit

Набор скриптов для автоматизации повседневных задач системного администрирования.

## Скрипты

| Скрипт | Что делает | Стек |
|---|---|---|
| `backup.py` | Бэкапит папку в архив с ротацией старых копий | Python 3 |
| `log_parser.py` | Парсит лог-файл, считает записи по уровням и топ сообщений | Python 3 |
| `disk_cleanup.py` | Удаляет файлы старше N дней по маске (dry-run поддерживается) | Python 3 |
| `bulk_setup.ps1` | Массово применяет DNS-настройки на списке удалённых машин | PowerShell |

## Требования

- Python 3.10+ (для .py скриптов, только стандартная библиотека)
- PowerShell 5.1+ и настроенный WinRM на целевых машинах (для `bulk_setup.ps1`)

## Примеры использования

### backup.py

```bash
python backup.py --src /home/user/data --dst /mnt/backups --keep 5
```

Бэкапит `/home/user/data` в zip-архив с меткой времени, хранит последние 5 архивов, старые удаляет автоматически.

### log_parser.py

```bash
python log_parser.py --file /var/log/syslog --level ERROR --top 10
```

Показывает сводку по уровням логирования и топ-10 самых частых ошибок.

### disk_cleanup.py

```bash
python disk_cleanup.py --path /tmp --days 14 --pattern "*.tmp" --dry-run
```

Сначала запускайте с `--dry-run`, чтобы увидеть, что будет удалено, прежде чем удалять по-настоящему.

### bulk_setup.ps1

```powershell
.\bulk_setup.ps1 -ComputerListPath .\hosts.txt -DnsServers "8.8.8.8","1.1.1.1"
```

Читает список машин из `hosts.txt` (по одному имени/IP на строку), применяет DNS-настройки, сохраняет CSV-отчёт по итогам.

## Структура репозитория

```
sysadmin-toolkit/
├── backup.py
├── log_parser.py
├── disk_cleanup.py
├── bulk_setup.ps1
├── requirements.txt
└── README.md
```
