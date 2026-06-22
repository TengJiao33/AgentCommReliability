param(
    [ValidateSet("PG40", "HSA", "Both")]
    [string]$Scope = "Both",
    [string]$BaseUrl = "",
    [string]$Model = "qwen2.5-14b-sseac-smoke",
    [string]$ApiKeyEnv = "OPENAI_API_KEY",
    [string]$ApiKey = "EMPTY",
    [int]$Pg40Limit = 5,
    [int]$HsaLimit = 3,
    [int]$MaxTokens = 2048,
    [double]$Temperature = 0.0,
    [string]$RunId = "",
    [string]$Python = "python",
    [switch]$IncludePrompts,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Resolve-BaseUrl {
    param([string]$ExplicitBaseUrl)
    if ($ExplicitBaseUrl) {
        return $ExplicitBaseUrl
    }
    foreach ($name in @("OPENAI_BASE_URL", "VLLM_BASE_URL", "LOCAL_OPENAI_BASE_URL", "A8002_BASE_URL")) {
        $value = [Environment]::GetEnvironmentVariable($name)
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return $value
        }
    }
    throw "No base URL supplied. Pass -BaseUrl or set OPENAI_BASE_URL / VLLM_BASE_URL / LOCAL_OPENAI_BASE_URL / A8002_BASE_URL."
}

function Join-Command {
    param([string]$Exe, [string[]]$CommandArgs)
    $parts = @($Exe)
    foreach ($arg in $CommandArgs) {
        if ($arg -match "\s") {
            $parts += '"' + ($arg -replace '"', '\"') + '"'
        } else {
            $parts += $arg
        }
    }
    return ($parts -join " ")
}

function Invoke-Step {
    param([string]$Exe, [string[]]$CommandArgs)
    $line = Join-Command -Exe $Exe -CommandArgs $CommandArgs
    Write-Host ">>> $line"
    if (-not $DryRun) {
        & $Exe @CommandArgs
    }
}

function New-RunId {
    param([string]$ModelName)
    $stamp = Get-Date -Format "yyyyMMdd-HHmm"
    $modelSlug = (($ModelName -replace "[^A-Za-z0-9]+", "-").Trim("-")).ToLowerInvariant()
    return "$stamp-local-sseac-smoke-queue-$modelSlug"
}

$resolvedBaseUrl = Resolve-BaseUrl -ExplicitBaseUrl $BaseUrl
if (-not [Environment]::GetEnvironmentVariable($ApiKeyEnv)) {
    [Environment]::SetEnvironmentVariable($ApiKeyEnv, $ApiKey, "Process")
}
if (-not $RunId) {
    $RunId = New-RunId -ModelName $Model
}

$runRoot = Join-Path "experiments" $RunId
$pg40Dir = Join-Path $runRoot "pg40"
$hsaDir = Join-Path $runRoot "hsa_v0"

Write-Host "[sseac-smoke-queue] scope=$Scope"
Write-Host "[sseac-smoke-queue] run_id=$RunId"
Write-Host "[sseac-smoke-queue] model=$Model"
Write-Host "[sseac-smoke-queue] base_url=$resolvedBaseUrl"
Write-Host "[sseac-smoke-queue] dry_run=$DryRun"

if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
    $manifest = [ordered]@{
        run_id = $RunId
        scope = $Scope
        model = $Model
        base_url = $resolvedBaseUrl
        pg40_limit = $Pg40Limit
        hsa_limit = $HsaLimit
        temperature = $Temperature
        max_tokens = $MaxTokens
        started_at = (Get-Date).ToString("o")
    }
    $manifest | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $runRoot "run_manifest.json") -Encoding UTF8
}

if ($Scope -in @("PG40", "Both")) {
    $pg40Packet = "experiments\20260618-local-sseac-v0-pg40-adapter\sseac_pg40_packet.jsonl"
    $pg40PgPacket = "experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl"
    $pg40Pred = Join-Path $pg40Dir "predictions_limit$Pg40Limit.jsonl"
    $pg40NoCompiler = Join-Path $pg40Dir "structured_no_compiler_limit$Pg40Limit.jsonl"
    $pg40NoCompilerSummary = Join-Path $pg40Dir "structured_no_compiler_summary_limit$Pg40Limit.json"
    $pg40NoCompilerScores = Join-Path $pg40Dir "scores_structured_no_compiler_limit$Pg40Limit.jsonl"
    $pg40NoCompilerScoreSummary = Join-Path $pg40Dir "summary_structured_no_compiler_limit$Pg40Limit.md"
    $pg40Compiled = Join-Path $pg40Dir "compiled_limit$Pg40Limit.jsonl"
    $pg40CompileSummary = Join-Path $pg40Dir "compile_summary_limit$Pg40Limit.json"
    $pg40Scores = Join-Path $pg40Dir "scores_limit$Pg40Limit.jsonl"
    $pg40Summary = Join-Path $pg40Dir "summary_limit$Pg40Limit.md"
    $pg40PairedDelta = Join-Path $pg40Dir "paired_delta_limit$Pg40Limit.json"
    $pg40PairedDeltaSummary = Join-Path $pg40Dir "paired_delta_limit$Pg40Limit.md"

    $pg40RunArgs = @(
        "scripts\run_sseac_v0_pg40_openai_compatible.py",
        "--packet", $pg40Packet,
        "--limit", [string]$Pg40Limit,
        "--base-url", $resolvedBaseUrl,
        "--model", $Model,
        "--out", $pg40Pred,
        "--temperature", [string]$Temperature,
        "--max-tokens", [string]$MaxTokens
    )
    if ($IncludePrompts) {
        $pg40RunArgs += "--include-prompts"
    }
    Invoke-Step -Exe $Python -CommandArgs $pg40RunArgs

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\compile_sseac_v0.py",
        "--packet", $pg40Packet,
        "--predictions", $pg40Pred,
        "--mode", "model_only",
        "--out", $pg40NoCompiler,
        "--summary-out", $pg40NoCompilerSummary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\score_sseac_pg40_compiled.py",
        "--pg-packet", $pg40PgPacket,
        "--compiled", $pg40NoCompiler,
        "--out", $pg40NoCompilerScores,
        "--summary-out", $pg40NoCompilerScoreSummary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\compile_sseac_v0.py",
        "--packet", $pg40Packet,
        "--predictions", $pg40Pred,
        "--mode", "compiler",
        "--out", $pg40Compiled,
        "--summary-out", $pg40CompileSummary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\score_sseac_pg40_compiled.py",
        "--pg-packet", $pg40PgPacket,
        "--compiled", $pg40Compiled,
        "--out", $pg40Scores,
        "--summary-out", $pg40Summary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\summarize_sseac_paired_delta.py",
        "--benchmark", "pg40",
        "--no-compiler-scores", $pg40NoCompilerScores,
        "--compiled-scores", $pg40Scores,
        "--out", $pg40PairedDelta,
        "--summary-out", $pg40PairedDeltaSummary
    )
}

if ($Scope -in @("HSA", "Both")) {
    $hsaPacket = "experiments\20260618-local-hsa-v0-sseac-adapter\hsa_v0_packet.jsonl"
    $hsaPred = Join-Path $hsaDir "predictions_limit$HsaLimit.jsonl"
    $hsaNoCompiler = Join-Path $hsaDir "structured_no_compiler_limit$HsaLimit.jsonl"
    $hsaNoCompilerSummary = Join-Path $hsaDir "structured_no_compiler_summary_limit$HsaLimit.json"
    $hsaNoCompilerScores = Join-Path $hsaDir "scores_structured_no_compiler_limit$HsaLimit.jsonl"
    $hsaNoCompilerScoreSummary = Join-Path $hsaDir "summary_structured_no_compiler_limit$HsaLimit.md"
    $hsaCompiled = Join-Path $hsaDir "compiled_limit$HsaLimit.jsonl"
    $hsaCompileSummary = Join-Path $hsaDir "compile_summary_limit$HsaLimit.json"
    $hsaScores = Join-Path $hsaDir "scores_limit$HsaLimit.jsonl"
    $hsaSummary = Join-Path $hsaDir "summary_limit$HsaLimit.md"
    $hsaPairedDelta = Join-Path $hsaDir "paired_delta_limit$HsaLimit.json"
    $hsaPairedDeltaSummary = Join-Path $hsaDir "paired_delta_limit$HsaLimit.md"

    $hsaRunArgs = @(
        "scripts\run_hsa_v0_sseac_openai_compatible.py",
        "--packet", $hsaPacket,
        "--limit", [string]$HsaLimit,
        "--base-url", $resolvedBaseUrl,
        "--model", $Model,
        "--out", $hsaPred,
        "--temperature", [string]$Temperature,
        "--max-tokens", [string]$MaxTokens
    )
    if ($IncludePrompts) {
        $hsaRunArgs += "--include-prompts"
    }
    Invoke-Step -Exe $Python -CommandArgs $hsaRunArgs

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\compile_sseac_v0.py",
        "--packet", $hsaPacket,
        "--predictions", $hsaPred,
        "--mode", "model_only",
        "--out", $hsaNoCompiler,
        "--summary-out", $hsaNoCompilerSummary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\score_hsa_v0_compiled.py",
        "--packet", $hsaPacket,
        "--compiled", $hsaNoCompiler,
        "--out", $hsaNoCompilerScores,
        "--summary-out", $hsaNoCompilerScoreSummary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\compile_sseac_v0.py",
        "--packet", $hsaPacket,
        "--predictions", $hsaPred,
        "--mode", "compiler",
        "--out", $hsaCompiled,
        "--summary-out", $hsaCompileSummary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\score_hsa_v0_compiled.py",
        "--packet", $hsaPacket,
        "--compiled", $hsaCompiled,
        "--out", $hsaScores,
        "--summary-out", $hsaSummary
    )

    Invoke-Step -Exe $Python -CommandArgs @(
        "scripts\summarize_sseac_paired_delta.py",
        "--benchmark", "hsa",
        "--no-compiler-scores", $hsaNoCompilerScores,
        "--compiled-scores", $hsaScores,
        "--out", $hsaPairedDelta,
        "--summary-out", $hsaPairedDeltaSummary
    )
}

Write-Host "[sseac-smoke-queue] done"
Write-Host "[sseac-smoke-queue] output_root=$runRoot"
