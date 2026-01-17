#!/usr/bin/env bash

MODEL=$1

if [ -z "$MODEL" ]; then
  echo "Usage: $0 <model_name>"
  exit 1
fi

# Datasets
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
  case $dataset in
    avatar)
      sources=("${source_languages_avatar[@]}")
      targets=("${target_languages_avatar[@]}")
      ;;
    evalplus)
      sources=("${source_languages_evalplus[@]}")
      targets=("${target_languages_evalplus[@]}")
      ;;
    codenet)
      sources=("${source_languages_codenet[@]}")
      targets=("${target_languages_codenet[@]}")
      ;;
    codenetintertrans)
      sources=("${source_languages_codenetintertrans[@]}")
      targets=("${target_languages_codenetintertrans[@]}")
      ;;
    *)
      echo "Unknown dataset: $dataset"
      continue
      ;;
  esac

  for src in "${sources[@]}"; do
    for tgt in "${targets[@]}"; do
      # Skip same-language translations
      if [ "$src" == "$tgt" ]; then
        continue
      fi

      echo "Running: dataset=$dataset, source=$src, target=$tgt, model=$MODEL"
      python prepare_sonarqube_translations.py \
        --dataset "$dataset" \
        --source_lang "$src" \
        --target_lang "$tgt" \
        --model "$MODEL"
    done
  done
done
