param(
    [int]$TotalRequests = 500,
    [int]$ConcurrentClients = 50,
    [string]$ExperimentID = "default"
)

$env:TOTAL_REQS = $TotalRequests
$env:CONCURRENT_CLIENTS = $ConcurrentClients
$env:EXPERIMENT_ID = $ExperimentID

docker-compose down -v

docker-compose up --build

Remove-Item Env:\TOTAL_REQS
Remove-Item Env:\CONCURRENT_CLIENTS
Remove-Item Env:\EXPERIMENT_ID