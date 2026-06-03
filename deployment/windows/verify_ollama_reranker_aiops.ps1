param(
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434",
    [string]$RerankerBaseUrl = "http://127.0.0.1:8002",
    [string]$EmbeddingModel = "bge-m3"
)

$ErrorActionPreference = "Stop"
$failures = 0

function Report {
    param([string]$Name, [bool]$Ok, [string]$Detail = "")
    if ($Ok) {
        Write-Host "[OK] $Name $Detail"
    } else {
        Write-Host "[FAIL] $Name $Detail"
        $script:failures += 1
    }
}

try {
    $tags = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -TimeoutSec 10
    $names = @($tags.models | ForEach-Object { $_.name })
    Report "Ollama tags" ($names.Count -gt 0) ($names -join ",")
    Report "Ollama model $EmbeddingModel" ($names -contains "${EmbeddingModel}:latest" -or $names -contains $EmbeddingModel)
} catch {
    Report "Ollama tags" $false $_.Exception.Message
}

try {
    $health = Invoke-RestMethod -Uri "$RerankerBaseUrl/health" -TimeoutSec 30
    Report "Reranker /health" ($health.reachable -eq $true) "model=$($health.model) dimension=$($health.dimension)"
} catch {
    Report "Reranker /health" $false $_.Exception.Message
}

try {
    $body = @{
        model = "bge-m3-embedding-reranker"
        query = "short video social media operations loop"
        documents = @("customer needs short video operations and social publishing loop", "database migration and port checks")
        top_n = 1
    } | ConvertTo-Json -Depth 5
    $result = Invoke-RestMethod -Uri "$RerankerBaseUrl/api/rerank" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 60
    Report "Reranker /api/rerank" ($result.ranked_indices[0] -eq 0) "scores=$($result.scores -join ',')"
} catch {
    Report "Reranker /api/rerank" $false $_.Exception.Message
}

if ($failures -gt 0) {
    throw "$failures Ollama/reranker verification checks failed"
}

Write-Host "SUMMARY: PASS"
