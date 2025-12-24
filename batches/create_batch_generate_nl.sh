#!/usr/bin/env bash

set -euo pipefail

TEMPLATE_FILE="generate_nl_template.sh"

datasets=("avatar" "codenet" "codenetintertrans")

source_languages_avatar=("Java" "Python")
source_languages_codenet=("C" "C++" "Go" "Python" "Java")
source_languages_evalplus=("Python")
source_languages_codenetintertrans=("C++" "Go" "Python" "Java")

for dataset in "${datasets[@]}"; do
    # Select the correct language array based on dataset
    case "$dataset" in
        avatar)
            langs=("${source_languages_avatar[@]}")
            ;;
        codenet)
            langs=("${source_languages_codenet[@]}")
            ;;
        codenetintertrans)
            langs=("${source_languages_codenetintertrans[@]}")
            ;;
        *)
            echo "Unknown dataset: $dataset"
            exit 1
            ;;
    esac

    for lang in "${langs[@]}"; do
        output_file="generate_nl_spec_${dataset}_${lang}.sh"

        sed \
            -e "s/##DATASET##/${dataset}/g" \
            -e "s/##LANG##/${lang}/g" \
            "$TEMPLATE_FILE" > "$output_file"

        chmod +x "$output_file"
        echo "Generated: $output_file"
    done
done
