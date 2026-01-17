#!/usr/bin/env bash

set -euo pipefail

TEMPLATE_FILE="template.sh"
MODEL=$1

datasets=("avatar" "codenet" "codenetintertrans" "evalplus")

# Dataset-specific language lists
source_languages_avatar=("Java" "Python")
target_languages_avatar=("C++" "C" "Java" "Go" "Python")

source_languages_evalplus=("Python")
target_languages_evalplus=("Java")

source_languages_codenet=("C" "C++" "Go" "Python" "Java")
target_languages_codenet=("C" "C++" "Go" "Python" "Java")

source_languages_codenetintertrans=("C++" "Go" "Python" "Java" "Javascript" "Rust")
target_languages_codenetintertrans=("C++" "Go" "Python" "Java" "Javascript" "Rust")

for dataset in "${datasets[@]}"; do
    case "$dataset" in
        avatar)
            source_languages=("${source_languages_avatar[@]}")
            target_languages=("${target_languages_avatar[@]}")
            ;;
        evalplus)
            source_languages=("${source_languages_evalplus[@]}")
            target_languages=("${target_languages_evalplus[@]}")
            ;;
        codenet)
            source_languages=("${source_languages_codenet[@]}")
            target_languages=("${target_languages_codenet[@]}")
            ;;
        codenetintertrans)
            source_languages=("${source_languages_codenetintertrans[@]}")
            target_languages=("${target_languages_codenetintertrans[@]}")
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

            output_file="generate_${MODEL}_${dataset}_${src_lang}_${tgt_lang}.sh"

            # Random node selection
            X=$((RANDOM % 4 + 1))
            sed_extra=(-e "s/########/#SBATCH -w virya${X}/g")

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
