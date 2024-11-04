$headers = @{
    "Content-Type" = "application/json"
}

for ($i = 1; $i -le 20; $i++) {
    $temperature = Get-Random -Minimum 15 -Maximum 35
    $humidity = Get-Random -Minimum 30 -Maximum 90
    $jsonData = @{
        "temperature" = "$temperature"
        "humidity" = "$humidity"
    } | ConvertTo-Json

    Invoke-WebRequest -Uri "http://10.0.0.24/receive" -Method POST -Headers $headers -Body $jsonData
    Write-Output "`n"
}
