param(
    [string]$GatewayBaseUrl = "http://localhost:8080",
    [string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-JsonRequest {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Url,
        [hashtable]$Headers,
        $Body
    )

    $invokeParams = @{
        Method      = $Method
        Uri         = $Url
        ErrorAction = "Stop"
    }

    if ($Headers) {
        $invokeParams.Headers = $Headers
    }

    if ($null -ne $Body) {
        $invokeParams.ContentType = "application/json"
        $invokeParams.Body = ($Body | ConvertTo-Json -Depth 10)
    }

    return Invoke-RestMethod @invokeParams
}

function Get-AuthHeaders {
    param([Parameter(Mandatory = $true)][string]$Token)

    return @{
        Authorization = "Bearer $Token"
    }
}

function Login-Role {
    param(
        [string]$Username,
        [string]$Password
    )

    return Invoke-JsonRequest -Method POST -Url "$GatewayBaseUrl/api/users/auth/login" -Body @{
        username = $Username
        password = $Password
    }
}

function Convert-ToCollection {
    param($Value)

    if ($null -eq $Value) {
        return @()
    }

    if ($Value -is [System.Array]) {
        if ($Value.Count -eq 1 -and $Value[0] -is [System.Array]) {
            return @($Value[0])
        }
        return @($Value)
    }

    return @($Value)
}

$customer = Login-Role -Username "customer" -Password "password123"
$staff = Login-Role -Username "staff" -Password "password123"
$admin = Login-Role -Username "admin" -Password "password123"

$customerHeaders = Get-AuthHeaders -Token $customer.access
$staffHeaders = Get-AuthHeaders -Token $staff.access
$adminHeaders = Get-AuthHeaders -Token $admin.access

$products = Convert-ToCollection (Invoke-JsonRequest -Method GET -Url "$GatewayBaseUrl/api/products/products")
if ($products.Count -eq 0) {
    throw "No products returned from catalog."
}

$selectedProduct = $products | Where-Object { [int]($_.stock) -gt 0 } | Select-Object -First 1
if (-not $selectedProduct) {
    throw "No in-stock product available for role flow verification."
}

Invoke-JsonRequest -Method POST -Url "$GatewayBaseUrl/api/cart/add" -Headers $customerHeaders -Body @{
    product_id = $selectedProduct.id
    quantity   = 1
} | Out-Null

$customerOrder = Invoke-JsonRequest -Method POST -Url "$GatewayBaseUrl/api/orders/" -Headers $customerHeaders -Body @{
    address = "99 Phase 9 Lane"
}

$paymentStatus = Invoke-JsonRequest -Method GET -Url "$GatewayBaseUrl/api/payments/status/$($customerOrder.id)" -Headers $customerHeaders
$shippingStatus = Invoke-JsonRequest -Method GET -Url "$GatewayBaseUrl/api/shipping/status/$($customerOrder.id)" -Headers $customerHeaders

$staffOrders = Convert-ToCollection (Invoke-JsonRequest -Method GET -Url "$GatewayBaseUrl/api/orders/" -Headers $staffHeaders)
$staffShippingBefore = Invoke-JsonRequest -Method GET -Url "$GatewayBaseUrl/api/shipping/status/$($customerOrder.id)" -Headers $staffHeaders
$staffShippingAfter = Invoke-JsonRequest -Method PATCH -Url "$GatewayBaseUrl/api/shipping/status/$($customerOrder.id)" -Headers $staffHeaders -Body @{
    status = "Delivered"
}
$staffOrderAfter = Invoke-JsonRequest -Method PATCH -Url "$GatewayBaseUrl/api/orders/$($customerOrder.id)" -Headers $staffHeaders -Body @{
    status = "Completed"
}

$adminUsers = Convert-ToCollection (Invoke-JsonRequest -Method GET -Url "$GatewayBaseUrl/api/users/users/" -Headers $adminHeaders)
$adminOrdersForCustomer = Convert-ToCollection (Invoke-JsonRequest -Method GET -Url "$GatewayBaseUrl/api/orders/?user_id=$($customer.user.id)" -Headers $adminHeaders)

$result = [ordered]@{
    verified_at = (Get-Date).ToString("o")
    customer = [ordered]@{
        user_id = $customer.user.id
        catalog_product_id = $selectedProduct.id
        order_id = $customerOrder.id
        order_status_after_create = $customerOrder.status
        payment_status = $paymentStatus.status
        shipping_status = $shippingStatus.status
    }
    staff = [ordered]@{
        user_id = $staff.user.id
        listed_orders = $staffOrders.Count
        shipping_status_before_update = $staffShippingBefore.status
        shipping_status_after_update = $staffShippingAfter.status
        order_status_after_update = $staffOrderAfter.status
    }
    admin = [ordered]@{
        user_id = $admin.user.id
        user_count = $adminUsers.Count
        filtered_orders_for_customer = $adminOrdersForCustomer.Count
    }
}

$json = $result | ConvertTo-Json -Depth 10

if ($OutputPath) {
    $directory = Split-Path -Path $OutputPath -Parent
    if ($directory) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    Set-Content -Path $OutputPath -Value $json -Encoding utf8
}

$json
