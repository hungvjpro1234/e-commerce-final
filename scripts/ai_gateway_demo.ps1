param(
    [string]$GatewayBaseUrl = "http://localhost:8080",
    [int]$UserId = 1,
    [string]$RecommendationQuery = "budget laptop",
    [string]$ChatMessage = "toi can laptop gia re",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

function Write-Step($message) {
    Write-Host "==> $message" -ForegroundColor Cyan
}

function Invoke-JsonRequest {
    param(
        [ValidateSet("GET", "POST", "PUT", "PATCH", "DELETE")]
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [object]$Body
    )

    $requestParams = @{
        Method      = $Method
        Uri         = $Url
        Headers     = $Headers
        ContentType = "application/json"
    }

    if ($null -ne $Body) {
        $requestParams.Body = ($Body | ConvertTo-Json -Depth 10)
    }

    return Invoke-RestMethod @requestParams
}

$gatewayHealthUrl = "$GatewayBaseUrl/health"
$recommendUrl = "$GatewayBaseUrl/api/ai/recommend?user_id=$UserId&limit=5&query=$([uri]::EscapeDataString($RecommendationQuery))"
$chatbotUrl = "$GatewayBaseUrl/api/ai/chatbot"
$behaviorUrl = "$GatewayBaseUrl/api/ai/behavior"

Write-Step "Checking gateway health"
$gatewayHealth = Invoke-JsonRequest -Method GET -Url $gatewayHealthUrl
if ($gatewayHealth.status -ne "ok") {
    throw "Gateway health check failed."
}

Write-Step "Tracking a behavior search event through gateway"
$behaviorEvent = Invoke-JsonRequest -Method POST -Url $behaviorUrl -Body @{
    user_id    = $UserId
    action     = "search"
    query_text = $RecommendationQuery
}

Write-Step "Requesting recommendations through gateway"
$recommendation = Invoke-JsonRequest -Method GET -Url $recommendUrl
if (-not $recommendation.items -or $recommendation.items.Count -lt 1) {
    throw "Recommendation response did not return any items."
}

Write-Step "Requesting chatbot response through gateway"
$chatbot = Invoke-JsonRequest -Method POST -Url $chatbotUrl -Body @{
    user_id = $UserId
    message = $ChatMessage
}

if (-not $chatbot.answer) {
    throw "Chatbot response did not return an answer."
}

$summary = [ordered]@{
    gateway_status               = $gatewayHealth.status
    behavior_event_id            = $behaviorEvent.id
    recommendation_user_id       = $recommendation.user_id
    recommendation_query         = $recommendation.query
    recommendation_total         = $recommendation.total
    top_recommendation_product   = $recommendation.items[0].name
    top_recommendation_category  = $recommendation.items[0].category
    top_recommendation_score     = $recommendation.items[0].score
    chatbot_query_type           = $chatbot.query_type
    chatbot_top_product          = $(if ($chatbot.products.Count -gt 0) { $chatbot.products[0].name } else { $null })
    chatbot_top_product_category = $(if ($chatbot.products.Count -gt 0) { $chatbot.products[0].category } else { $null })
    chatbot_context_count        = $chatbot.retrieved_context.Count
}

$summaryJson = $summary | ConvertTo-Json -Depth 8

if ($OutputPath) {
    $outputDir = Split-Path -Parent $OutputPath
    if ($outputDir) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    Set-Content -Path $OutputPath -Value $summaryJson -Encoding UTF8
    Write-Step "Saved summary to $OutputPath"
}

Write-Step "AI gateway demo completed successfully"
$summaryJson
