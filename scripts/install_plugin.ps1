[CmdletBinding()]
param(
    [string]$Source = "https://github.com/gerbson-itegra/vervit-assistant.git",
    [string]$Ref = "main"
)

$ErrorActionPreference = "Stop"
$marketplaceName = "vervit"
$pluginName = "vervit-assistant"

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw "O CLI 'codex' nao foi encontrado no PATH."
}

function Invoke-Codex {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments,
        [switch]$CaptureOutput
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        if ($CaptureOutput) {
            $output = & codex @Arguments 2>&1 | Out-String
        } else {
            & codex @Arguments
            $output = $null
        }
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    if ($exitCode -ne 0) {
        throw "Falha ao executar 'codex $($Arguments -join ' ')': $output"
    }

    return $output
}

$configuredMarketplaces = Invoke-Codex -Arguments @("plugin", "marketplace", "list") -CaptureOutput
$marketplaceConfigured = ($configuredMarketplaces -split "\r?\n") |
    Select-String -Pattern "^\s*$([regex]::Escape($marketplaceName))\s+" -Quiet

if ($marketplaceConfigured) {
    if (Test-Path -LiteralPath $Source) {
        Write-Host "Marketplace local '$marketplaceName' ja configurado."
    } else {
        Write-Host "Atualizando marketplace '$marketplaceName'..."
        Invoke-Codex -Arguments @("plugin", "marketplace", "upgrade", $marketplaceName)
    }
} else {
    Write-Host "Adicionando marketplace '$marketplaceName' de '$Source'..."
    if (Test-Path -LiteralPath $Source) {
        Invoke-Codex -Arguments @(
            "plugin",
            "marketplace",
            "add",
            (Resolve-Path -LiteralPath $Source).Path
        )
    } else {
        Invoke-Codex -Arguments @("plugin", "marketplace", "add", $Source, "--ref", $Ref)
    }
}

Write-Host "Instalando '$pluginName@$marketplaceName'..."
Invoke-Codex -Arguments @("plugin", "add", "$pluginName@$marketplaceName")

Write-Host "Vervit Assistant instalado. Abra uma nova thread no Codex para usa-lo."
