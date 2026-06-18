param(
    [string]$SshHost = "A800_2",
    [string]$Workspace = "/data/xuhaoming/yfy/research_workspace",
    [string]$GpuId = "7",
    [string]$Port = "8047",
    [int]$Limit = 12,
    [int]$MaxTokens = 320,
    [int]$RequestTimeout = 240,
    [int]$RunTimeout = 14400,
    [switch]$IncludePrompts,
    [string]$RunId = "",
    [string]$Conditions = "shared_only full_info oracle_public_facts exchange_then_decide fact_only_with_options_exchange blind_exchange blind_minimal_exchange fact_only_exchange",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $RunId) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmm"
    $scope = if ($Limit -ge 65) { "full$Limit" } else { "smoke$Limit" }
    $RunId = "$stamp-a8002-hiddenbench-v2-stage3-blind-sender-$scope-qwen25-14b"
}

$includePromptsValue = if ($IncludePrompts) { "1" } else { "0" }

$remoteScript = @"
set -euo pipefail
cd "$Workspace"
echo "[stage3] run_id=$RunId"
echo "[stage3] gpu=$GpuId port=$Port limit=$Limit max_tokens=$MaxTokens"
echo "[stage3] conditions=$Conditions"
GPU_ID="$GpuId" \
PORT="$Port" \
RUN_ID="$RunId" \
LIMIT="$Limit" \
MAX_TOKENS="$MaxTokens" \
REQUEST_TIMEOUT="$RequestTimeout" \
RUN_TIMEOUT="$RunTimeout" \
INCLUDE_PROMPTS="$includePromptsValue" \
CONDITIONS="$Conditions" \
bash scripts/run_hiddenbench_probe_a8002.sh
"@

if ($DryRun) {
    $remoteScript
    exit 0
}

$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($remoteScript))
ssh $SshHost "bash -lc 'echo $encoded | base64 -d | bash'"
