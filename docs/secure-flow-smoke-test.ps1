param(
    [string]$BaseUserUrl = "http://localhost:8002",
    [string]$BaseCartUrl = "http://localhost:8003",
    [string]$BaseOrderUrl = "http://localhost:8004",
    [string]$BasePaymentUrl = "http://localhost:8005",
    [string]$BaseShippingUrl = "http://localhost:8006",
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

function Get-AuthHeaders($token) {
    return @{
        Authorization   = "Bearer $token"
        "X-Correlation-ID" = [guid]::NewGuid().ToString()
    }
}

$customerAUsername = "customer"
$customerAPassword = "password123"
$customerBUsername = "customerb"
$customerBPassword = "password123"

Write-Step "Logging in seeded customer A"
$customerALogin = Invoke-JsonRequest -Method POST -Url "$BaseUserUrl/auth/login" -Body @{
    username = $customerAUsername
    password = $customerAPassword
}
$customerAToken = $customerALogin.access
$customerAHeaders = Get-AuthHeaders -token $customerAToken

Write-Step "Ensuring customer B exists"
try {
    Invoke-JsonRequest -Method POST -Url "$BaseUserUrl/auth/register" -Body @{
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

Write-Step "Logging in customer B"
$customerBLogin = Invoke-JsonRequest -Method POST -Url "$BaseUserUrl/auth/login" -Body @{
    username = $customerBUsername
    password = $customerBPassword
}
$customerBToken = $customerBLogin.access
$customerBHeaders = Get-AuthHeaders -token $customerBToken

Write-Step "Adding one product to customer A cart"
Invoke-JsonRequest -Method POST -Url "$BaseCartUrl/cart/add" -Headers $customerAHeaders -Body @{
    product_id = 1
    quantity   = 1
} | Out-Null

Write-Step "Fetching customer A cart"
$cart = Invoke-JsonRequest -Method GET -Url "$BaseCartUrl/cart/" -Headers $customerAHeaders
if (-not $cart.items -or $cart.items.Count -lt 1) {
    throw "Customer A cart is empty; expected at least one item."
}

Write-Step "Creating order from customer A cart"
$order = Invoke-JsonRequestAllowFailureStatus -Method POST -Url "$BaseOrderUrl/orders/" -AllowedStatusCodes @(402) -Headers $customerAHeaders -Body @{
    address                  = "123 Secure Flow Street"
    simulate_payment_failure = [bool]$SimulatePaymentFailure
}

if (-not $order.id) {
    throw "Order creation did not return an order id."
}

Write-Step "Fetching order as owner"
$ownerOrder = Invoke-JsonRequest -Method GET -Url "$BaseOrderUrl/orders/$($order.id)/" -Headers $customerAHeaders

Write-Step "Checking payment status as owner"
$paymentStatus = Invoke-JsonRequest -Method GET -Url "$BasePaymentUrl/payment/status/$($order.id)" -Headers $customerAHeaders

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

    Write-Step "Checking shipping status as owner"
    $shippingStatus = Invoke-JsonRequest -Method GET -Url "$BaseShippingUrl/shipping/status/$($order.id)" -Headers $customerAHeaders
    if ($shippingStatus.status -notin @("Processing", "Shipping", "Delivered")) {
        throw "Unexpected shipping status '$($shippingStatus.status)'."
    }

    Write-Step "Verifying customer B cannot access customer A order/payment/shipping"
    Invoke-JsonExpectFailure -Method GET -Url "$BaseOrderUrl/orders/$($order.id)/" -ExpectedStatus 404 -Headers $customerBHeaders
    Invoke-JsonExpectFailure -Method GET -Url "$BasePaymentUrl/payment/status/$($order.id)" -ExpectedStatus 404 -Headers $customerBHeaders
    Invoke-JsonExpectFailure -Method GET -Url "$BaseShippingUrl/shipping/status/$($order.id)" -ExpectedStatus 404 -Headers $customerBHeaders
}

Write-Step "Smoke test completed successfully"
$summary = [ordered]@{
    order_id        = $order.id
    order_status    = $ownerOrder.status
    payment_status  = $paymentStatus.status
    simulated_fail  = [bool]$SimulatePaymentFailure
}

if ($shippingStatus) {
    $summary.shipping_status = $shippingStatus.status
}

$summary | ConvertTo-Json -Depth 5
