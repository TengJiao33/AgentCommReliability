param(
    [string]$SshHost = "A800_2",
    [string]$Workspace = "/data/xuhaoming/yfy/research_workspace",
    [string]$GpuId = "7",
    [string]$Port = "8053",
    [string]$ModelPath = "/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct",
    [string]$ServedModel = "qwen2.5-14b-hiddenbench",
    [int]$Limit = 12,
    [int]$MaxTokens = 320,
    [int]$RequestTimeout = 240,
    [int]$RunTimeout = 18000,
    [switch]$IncludePrompts,
    [string]$RunId = "",
    [string]$Conditions = "shared_only full_info oracle_public_facts exchange_then_decide blind_minimal_exchange private_plus_task_minimal_exchange private_plus_options_minimal_exchange private_plus_shared_minimal_exchange full_visibility_minimal_exchange fact_only_exchange",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $RunId) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmm"
    $scope = if ($Limit -ge 65) { "full$Limit" } else { "smoke$Limit" }
    $modelSlug = ($ServedModel -replace '[^A-Za-z0-9]+', '-').Trim('-').ToLowerInvariant()
    $RunId = "$stamp-a8002-hiddenbench-v2-stage4-sender-visibility-$scope-$modelSlug"
}

$includePromptsValue = if ($IncludePrompts) { "1" } else { "0" }

$remoteScript = @"
set -euo pipefail
cd "$Workspace"
echo "[stage4] run_id=$RunId"
echo "[stage4] model_path=$ModelPath served_model=$ServedModel"
echo "[stage4] gpu=$GpuId port=$Port limit=$Limit max_tokens=$MaxTokens"
echo "[stage4] conditions=$Conditions"
MODEL_PATH="$ModelPath" \
SERVED_MODEL="$ServedModel" \
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
