param(
    [string]$GatewayBaseUrl = "http://localhost:8080",
    [int]$Iterations = 10,
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

function Measure-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url
    )

    $samples = @()
    for ($i = 0; $i -lt $Iterations; $i++) {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        Invoke-RestMethod -Method $Method -Uri $Url | Out-Null
        $sw.Stop()
        $samples += [math]::Round($sw.Elapsed.TotalMilliseconds, 2)
    }

    $ordered = $samples | Sort-Object
    $average = [math]::Round((($samples | Measure-Object -Average).Average), 2)
    $minimum = [math]::Round($ordered[0], 2)
    $maximum = [math]::Round($ordered[-1], 2)
    $index95 = [math]::Ceiling($ordered.Count * 0.95) - 1
    if ($index95 -lt 0) { $index95 = 0 }
    $p95 = [math]::Round($ordered[$index95], 2)
    $throughputRps = if ($average -gt 0) { [math]::Round(1000 / $average, 2) } else { $null }

    return [ordered]@{
        name = $Name
        method = $Method
        url = $Url
        iterations = $Iterations
        avg_ms = $average
        min_ms = $minimum
        p95_ms = $p95
        max_ms = $maximum
        approx_rps_single_client = $throughputRps
        samples_ms = $samples
    }
}

$results = @(
    (Measure-Endpoint -Name "gateway_health" -Method "GET" -Url "$GatewayBaseUrl/health"),
    (Measure-Endpoint -Name "product_catalog" -Method "GET" -Url "$GatewayBaseUrl/api/products/products"),
    (Measure-Endpoint -Name "ai_recommend" -Method "GET" -Url "$GatewayBaseUrl/api/ai/recommend?user_id=1&limit=5&query=budget%20laptop")
)

$payload = [ordered]@{
    measured_at = (Get-Date).ToString("o")
    gateway_base_url = $GatewayBaseUrl
    iterations = $Iterations
    results = $results
}

$json = $payload | ConvertTo-Json -Depth 10

if ($OutputPath) {
    $outputDir = Split-Path -Parent $OutputPath
    if ($outputDir) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    Set-Content -Path $OutputPath -Value $json -Encoding UTF8
}

$json
