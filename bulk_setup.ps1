<#
.SYNOPSIS
    Массовая настройка DNS-серверов на списке удалённых машин.

.DESCRIPTION
    Читает список хостов из текстового файла и применяет заданные DNS-серверы
    через Invoke-Command. Требует настроенный WinRM на целевых машинах и права
    администратора. По итогам выполнения сохраняет CSV-отчёт.

.PARAMETER ComputerListPath
    Путь к текстовому файлу со списком имён компьютеров/IP, по одному на строку.

.PARAMETER DnsServers
    Список DNS-серверов через запятую.

.PARAMETER Credential
    Учётные данные для подключения. Если не указаны — будут запрошены интерактивно.

.EXAMPLE
    .\bulk_setup.ps1 -ComputerListPath .\hosts.txt -DnsServers "8.8.8.8","1.1.1.1"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ComputerListPath,

    [Parameter(Mandatory = $true)]
    [string[]]$DnsServers,

    [Parameter(Mandatory = $false)]
    [System.Management.Automation.PSCredential]$Credential
)

if (-not (Test-Path $ComputerListPath)) {
    Write-Error "Файл со списком компьютеров не найден: $ComputerListPath"
    exit 1
}

if (-not $Credential) {
    $Credential = Get-Credential -Message "Учётные данные для подключения к удалённым машинам"
}

$computers = Get-Content $ComputerListPath | Where-Object { $_.Trim() -ne "" }
$results = @()

foreach ($computer in $computers) {
    Write-Host "Обрабатываю $computer ..." -ForegroundColor Cyan

    try {
        $result = Invoke-Command -ComputerName $computer -Credential $Credential -ScriptBlock {
            param($dns)
            $adapters = Get-DnsClient | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }
            foreach ($adapter in $adapters) {
                Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses $dns
            }
            return "OK"
        } -ArgumentList (,$DnsServers) -ErrorAction Stop

        $results += [PSCustomObject]@{ Computer = $computer; Status = "Успешно"; Details = $result }
        Write-Host "  Успешно" -ForegroundColor Green
    }
    catch {
        $results += [PSCustomObject]@{ Computer = $computer; Status = "Ошибка"; Details = $_.Exception.Message }
        Write-Host "  Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== Итоги ===" -ForegroundColor Yellow
$results | Format-Table -AutoSize

$reportPath = "bulk_setup_report_{0}.csv" -f (Get-Date -Format "yyyyMMdd_HHmmss")
$results | Export-Csv -Path $reportPath -NoTypeInformation -Encoding UTF8
Write-Host "Отчёт сохранён: $reportPath"
