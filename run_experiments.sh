#!/bin/bash

declare -a experiments=(
    "TOTAL_REQS=500 EXPERIMENT_ID=small"
    "TOTAL_REQS=5000 EXPERIMENT_ID=medium"
    "TOTAL_REQS=50000 EXPERIMENT_ID=large"
)

for exp in "${experiments[@]}"; do
    echo "Iniciando experimento: $exp"
    docker-compose down -v
    
    # Para Windows (PowerShell), substitua por:
    # $env:TOTAL_REQS=500; $env:EXPERIMENT_ID="small"
    export $exp
    
    docker-compose up --build
    
    echo "Pausa entre experimentos..."
    sleep 60
done

echo "Todos experimentos concluídos! Verifique o diretório ./results"