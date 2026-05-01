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

    $response = Invoke-RestMethod @invokeParams
    return $response
}

function Invoke-ExpectStatus {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][int]$ExpectedStatus,
        [hashtable]$Headers,
        $Body
    )

    try {
        Invoke-JsonRequest -Method $Method -Url $Url -Headers $Headers -Body $Body | Out-Null
        throw "Expected HTTP $ExpectedStatus from $Url but request succeeded."
    }
    catch {
        $statusCode = -1
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }

        if ($statusCode -ne $ExpectedStatus) {
            throw "Expected HTTP $ExpectedStatus from $Url but received HTTP $statusCode."
        }

        return $statusCode
    }
}

function Get-AuthHeaders {
    param([Parameter(Mandatory = $true)][string]$Token)

    return @{
        Authorization = "Bearer $Token"
    }
}

$loginUrl = "$GatewayBaseUrl/api/users/auth/login"
$cartUrl = "$GatewayBaseUrl/api/cart/"
$adminUsersUrl = "$GatewayBaseUrl/api/users/users/"

$customerLogin = Invoke-JsonRequest -Method POST -Url $loginUrl -Body @{
    username = "customer"
    password = "password123"
}

$adminLogin = Invoke-JsonRequest -Method POST -Url $loginUrl -Body @{
    username = "admin"
    password = "password123"
}

if (-not $customerLogin.access) {
    throw "Customer login did not return an access token."
}

if (-not $adminLogin.access) {
    throw "Admin login did not return an access token."
}

$customerHeaders = Get-AuthHeaders -Token $customerLogin.access
$adminHeaders = Get-AuthHeaders -Token $adminLogin.access

$protectedRouteWithoutToken = Invoke-ExpectStatus -Method GET -Url $cartUrl -ExpectedStatus 401
$adminRouteWithCustomerToken = Invoke-ExpectStatus -Method GET -Url $adminUsersUrl -ExpectedStatus 403 -Headers $customerHeaders
$adminUsers = Invoke-JsonRequest -Method GET -Url $adminUsersUrl -Headers $adminHeaders

$result = [ordered]@{
    gateway_base_url = $GatewayBaseUrl
    login_returns_token = $true
    customer_token_claims = @{
        has_access = [bool]$customerLogin.access
        has_refresh = [bool]$customerLogin.refresh
    }
    protected_route_without_token_status = $protectedRouteWithoutToken
    admin_route_with_customer_token_status = $adminRouteWithCustomerToken
    admin_route_with_admin_token_status = 200
    admin_user_count = @($adminUsers).Count
    verified_at = (Get-Date).ToString("o")
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
