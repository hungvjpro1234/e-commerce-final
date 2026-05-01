param(
    [string]$GatewayBaseUrl = "http://localhost:8080",
    [string]$OutputPath = "",
    [switch]$SimulatePaymentFailure
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

function Invoke-JsonRequestAllowFailureStatus {
    param(
        [ValidateSet("GET", "POST", "PUT", "PATCH", "DELETE")]
        [string]$Method,
        [string]$Url,
        [int[]]$AllowedStatusCodes,
        [hashtable]$Headers = @{},
        [object]$Body
    )

    try {
        return Invoke-JsonRequest -Method $Method -Url $Url -Headers $Headers -Body $Body
    }
    catch {
        $response = $_.Exception.Response
        if (-not $response) {
            throw
        }

        $statusCode = $response.StatusCode.value__
        if ($statusCode -notin $AllowedStatusCodes) {
            throw
        }

        $content = $_.ErrorDetails.Message
        if (-not $content) {
            $stream = $response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $content = $reader.ReadToEnd()
            $reader.Dispose()
        }
        return $content | ConvertFrom-Json
    }
}

function Invoke-JsonExpectFailure {
    param(
        [ValidateSet("GET", "POST", "PUT", "PATCH", "DELETE")]
        [string]$Method,
        [string]$Url,
        [int]$ExpectedStatus,
        [hashtable]$Headers = @{},
        [object]$Body
    )

    try {
        Invoke-JsonRequest -Method $Method -Url $Url -Headers $Headers -Body $Body | Out-Null
        throw "Expected HTTP $ExpectedStatus from $Url but request succeeded."
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -ne $ExpectedStatus) {
            throw "Expected HTTP $ExpectedStatus from $Url but got $statusCode. $($_.Exception.Message)"
        }
    }
}

function Get-AuthHeaders($token) {
    return @{
        Authorization    = "Bearer $token"
        "X-Correlation-ID" = [guid]::NewGuid().ToString()
    }
}

$gatewayHealthUrl = "$GatewayBaseUrl/health"
$loginUrl = "$GatewayBaseUrl/api/users/auth/login"
$registerUrl = "$GatewayBaseUrl/api/users/auth/register"
$productsUrl = "$GatewayBaseUrl/api/products/products"
$cartAddUrl = "$GatewayBaseUrl/api/cart/add"
$cartUrl = "$GatewayBaseUrl/api/cart/"
$ordersUrl = "$GatewayBaseUrl/api/orders/"
$paymentsStatusBaseUrl = "$GatewayBaseUrl/api/payments/status"
$shippingStatusBaseUrl = "$GatewayBaseUrl/api/shipping/status"

$customerAUsername = "customer"
$customerAPassword = "password123"
$customerBUsername = "customerb"
$customerBPassword = "password123"

Write-Step "Checking gateway health"
$gatewayHealth = Invoke-JsonRequest -Method GET -Url $gatewayHealthUrl
if ($gatewayHealth.status -ne "ok") {
    throw "Gateway health check failed."
}

Write-Step "Logging in seeded customer A through gateway"
$customerALogin = Invoke-JsonRequest -Method POST -Url $loginUrl -Body @{
    username = $customerAUsername
    password = $customerAPassword
}
$customerAToken = $customerALogin.access
$customerAHeaders = Get-AuthHeaders -token $customerAToken

Write-Step "Ensuring customer B exists through gateway"
try {
    Invoke-JsonRequest -Method POST -Url $registerUrl -Body @{
        username = $customerBUsername
        email    = "customerb@example.com"
        password = $customerBPassword
        role     = "customer"
    } | Out-Null
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -notin @(400, 409)) {
        throw
    }
}

Write-Step "Logging in customer B through gateway"
$customerBLogin = Invoke-JsonRequest -Method POST -Url $loginUrl -Body @{
    username = $customerBUsername
    password = $customerBPassword
}
$customerBToken = $customerBLogin.access
$customerBHeaders = Get-AuthHeaders -token $customerBToken

Write-Step "Browsing product catalog through gateway"
$products = Invoke-JsonRequest -Method GET -Url $productsUrl
if (-not $products -or $products.Count -lt 1) {
    throw "Product catalog is empty; expected at least one product."
}

$selectedProduct = $products | Where-Object { $_.stock -ge 1 } | Select-Object -First 1
if (-not $selectedProduct) {
    throw "No in-stock product found for checkout flow."
}

Write-Step "Adding selected product to customer A cart"
Invoke-JsonRequest -Method POST -Url $cartAddUrl -Headers $customerAHeaders -Body @{
    product_id = $selectedProduct.id
    quantity   = 1
} | Out-Null

Write-Step "Fetching customer A cart through gateway"
$cart = Invoke-JsonRequest -Method GET -Url $cartUrl -Headers $customerAHeaders
if (-not $cart.items -or $cart.items.Count -lt 1) {
    throw "Customer A cart is empty after add-to-cart."
}

$cartItem = $cart.items | Where-Object { $_.product_id -eq $selectedProduct.id } | Select-Object -First 1
if (-not $cartItem) {
    throw "Selected product is not present in the cart."
}

Write-Step "Creating order through gateway"
$order = Invoke-JsonRequestAllowFailureStatus -Method POST -Url $ordersUrl -AllowedStatusCodes @(402) -Headers $customerAHeaders -Body @{
    address                  = "123 Chapter 4 Demo Street"
    simulate_payment_failure = [bool]$SimulatePaymentFailure
}

if (-not $order.id) {
    throw "Order creation did not return an order id."
}

Write-Step "Fetching order as owner through gateway"
$ownerOrder = Invoke-JsonRequest -Method GET -Url "$ordersUrl$($order.id)/" -Headers $customerAHeaders

Write-Step "Checking payment status through gateway"
$paymentStatus = Invoke-JsonRequest -Method GET -Url "$paymentsStatusBaseUrl/$($order.id)" -Headers $customerAHeaders

$summary = [ordered]@{
    gateway_status        = $gatewayHealth.status
    product_id            = $selectedProduct.id
    product_name          = $selectedProduct.name
    cart_item_quantity    = $cartItem.quantity
    order_id              = $order.id
    order_status          = $ownerOrder.status
    payment_status        = $paymentStatus.status
    simulated_fail        = [bool]$SimulatePaymentFailure
}

if ($SimulatePaymentFailure) {
    if ($ownerOrder.status -ne "Cancelled") {
        throw "Expected cancelled order on simulated payment failure, got '$($ownerOrder.status)'."
    }
    if ($paymentStatus.status -ne "Failed") {
        throw "Expected failed payment on simulated payment failure, got '$($paymentStatus.status)'."
    }
}
else {
    if ($paymentStatus.status -ne "Success") {
        throw "Expected successful payment, got '$($paymentStatus.status)'."
    }

    Write-Step "Checking shipping status through gateway"
    $shippingStatus = Invoke-JsonRequest -Method GET -Url "$shippingStatusBaseUrl/$($order.id)" -Headers $customerAHeaders
    if ($shippingStatus.status -notin @("Processing", "Shipping", "Delivered")) {
        throw "Unexpected shipping status '$($shippingStatus.status)'."
    }

    Write-Step "Verifying customer B cannot access customer A order, payment, and shipping data"
    Invoke-JsonExpectFailure -Method GET -Url "$ordersUrl$($order.id)/" -ExpectedStatus 404 -Headers $customerBHeaders
    Invoke-JsonExpectFailure -Method GET -Url "$paymentsStatusBaseUrl/$($order.id)" -ExpectedStatus 404 -Headers $customerBHeaders
    Invoke-JsonExpectFailure -Method GET -Url "$shippingStatusBaseUrl/$($order.id)" -ExpectedStatus 404 -Headers $customerBHeaders

    $summary.shipping_status = $shippingStatus.status
}

Write-Step "Chapter 4 checkout flow completed successfully"
$summaryJson = $summary | ConvertTo-Json -Depth 8

if ($OutputPath) {
    $outputDir = Split-Path -Parent $OutputPath
    if ($outputDir) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    Set-Content -Path $OutputPath -Value $summaryJson -Encoding UTF8
    Write-Step "Saved summary to $OutputPath"
}

$summaryJson
