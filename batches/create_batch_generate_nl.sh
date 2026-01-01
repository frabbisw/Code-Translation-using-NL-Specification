#!/usr/bin/env bash

set -euo pipefail

TEMPLATE_FILE="template.sh"
MODEL="magicoder"

datasets=("avatar" "codenet" "codenetintertrans")

target_languages=("C++" "C" "Java" "Go" "Python")

source_languages_avatar=("Java" "Python")
source_languages_codenet=("C" "C++" "Go" "Python" "Java")
source_languages_codenetintertrans=("C++" "Go" "Python" "Java")

for dataset in "${datasets[@]}"; do
    case "$dataset" in
        avatar)
            source_languages=("${source_languages_avatar[@]}")
            ;;
        codenet)
            source_languages=("${source_languages_codenet[@]}")
            ;;
        codenetintertrans)
            source_languages=("${source_languages_codenetintertrans[@]}")
            ;;
        *)
            echo "Unknown dataset: $dataset"
            exit 1
            ;;
    esac

    for src_lang in "${source_languages[@]}"; do
        for tgt_lang in "${target_languages[@]}"; do
            if [[ "$src_lang" == "$tgt_lang" ]]; then
                continue
            fi

            output_file="generate_${dataset}_${src_lang}_${tgt_lang}.sh"

            # Decide replacement for ########
            sed_extra=()
            if [[ "$tgt_lang" == "C" || "$tgt_lang" == "C++" ]]; then
                X=$((RANDOM % 4 + 1))
                sed_extra+=(-e "s/########/#SBATCH -w virya${X}/g")
            fi

            sed \
                -e "s/##DATASET##/${dataset}/g" \
                -e "s/##SRC_LANG##/${src_lang}/g" \
                -e "s/##TGT_LANG##/${tgt_lang}/g" \
                -e "s/##MODEL##/${MODEL}/g" \
                "${sed_extra[@]}" \
                "$TEMPLATE_FILE" > "$output_file"

            chmod +x "$output_file"
        done
    done
done
