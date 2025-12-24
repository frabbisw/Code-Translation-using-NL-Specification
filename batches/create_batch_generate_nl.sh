#!/bin/bash

datasets=("avatar" "codenet" "codenetintertrans")
source_languages_avatar=("Java" "Python")
source_languages_codenet=("C" "C++" "Go" "Python" "Java")
source_languages_evalplus=("Python") 
source_languages_codenet_intertrans=("C++" "Go" "Python" "Java")

TEMPLATE_FILE="generate_nl_template.sh"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file '$TEMPLATE_FILE' not found!"
    exit 1
fi

for dataset in "${datasets[@]}"; do
    case "$dataset" in
        "avatar")
            current_langs=("${source_languages_avatar[@]}")
            ;;
        "codenet")
            current_langs=("${source_languages_codenet[@]}")
            ;;
        "codenetintertrans")
            current_langs=("${source_languages_codenet_intertrans[@]}")
            ;;
        "evalplus")
            current_langs=("${source_languages_evalplus[@]}")
            ;;
        *)
            echo "Warning: No languages defined for dataset '$dataset'. Skipping."
            continue
            ;;
    esac

    for lang in "${current_langs[@]}"; do
        output_file="generate_nl_spec_${dataset}_${lang}.sh"

        echo "Generating $output_file..."

        sed -e "s/##DATASET##/$dataset/g" \
            -e "s/##LANG##/$lang/g" \
            "$TEMPLATE_FILE" > "$output_file"

        chmod +x "$output_file"
    done
done

echo "All scripts generated successfully."
