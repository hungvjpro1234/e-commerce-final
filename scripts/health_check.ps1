param(
    [string]$GatewayBaseUrl = "http://localhost:8080",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

function Invoke-JsonRequest {
    param(
        [ValidateSet("GET")]
        [string]$Method,
        [string]$Url
    )

    return Invoke-RestMethod -Method $Method -Uri $Url
}

$targets = [ordered]@{
    gateway          = "$GatewayBaseUrl/health"
    user_service     = "$GatewayBaseUrl/api/users/health"
    product_service  = "$GatewayBaseUrl/api/products/health"
    cart_service     = "$GatewayBaseUrl/api/cart/health"
    order_service    = "$GatewayBaseUrl/api/orders/health"
    payment_service  = "$GatewayBaseUrl/api/payments/health"
    shipping_service = "$GatewayBaseUrl/api/shipping/health"
    ai_service       = "$GatewayBaseUrl/api/ai/health"
}

$results = [ordered]@{}

foreach ($entry in $targets.GetEnumerator()) {
    $response = Invoke-JsonRequest -Method GET -Url $entry.Value
    $results[$entry.Key] = $response
}

$output = $results | ConvertTo-Json -Depth 8

if ($OutputPath) {
    $outputDir = Split-Path -Parent $OutputPath
    if ($outputDir) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    Set-Content -Path $OutputPath -Value $output -Encoding UTF8
}

$output
