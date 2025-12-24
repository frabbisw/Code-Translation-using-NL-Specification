#!/bin/bash

# Define the datasets, languages, and models
datasets=("avatar" "codenet" "codenetintertrans")
source_languages_avatar=("Java" "Python")
source_languages_codenet=("C" "C++" "Go" "Python" "Java")
source_languages_evalplus=("Python")
source_languages_codenet_intertrans=("C++" "Go" "Python" "Java")

# models=("GPT-4o-mini" "GPT-4")
models=("gpt-4o-mini")

model=$1
model_dir=$2
src_dataset=$3
src_lang=$4

# Declare an associative array
declare -A languages

# Initialize the associative array with key-value pairs
languages=(
    [Python]="py"
    [Java]="java"
    [C++]="cpp"
    [C]="c"
    [Go]="go"
)


# Function to perform translation
pseudocode_generation() {
  local dataset=$1
  local source_lang=$2
  local filename=$3

  echo "Generating Pseudocode of $source_lang in dataset $dataset using model $model..."
  python pseudocode_generation.py --dataset "$dataset" --source_lang "$source_lang" --filename "$filename" --model "$model" --models_dir "$model_dir"
}

# # Translate for avatar dataset
# for source_lang in "${source_languages_avatar[@]}"; do
#   for file in dataset/avatar/$source_lang/Code/*.${languages[$source_lang]}; do
#     base_name=$(basename "$file" .${languages[$source_lang]}).${languages[$source_lang]}
#     pseudocode_generation "avatar" "$source_lang" "$base_name"
#   done
# done

# # Translate for codenet dataset
# for source_lang in "${source_languages_codenet[@]}"; do
#   for file in dataset/codenet/$source_lang/Code/*.${languages[$source_lang]}; do
#     base_name=$(basename "$file" .${languages[$source_lang]}).${languages[$source_lang]}
#     pseudocode_generation "codenet" "$source_lang" "$base_name"
#   done
# done

# Translate for codenet(InterTrans) dataset
for file in dataset/$src_dataset/$src_lang/Code/*.${languages[$src_lang]}; do
  base_name=$(basename "$file" .${languages[$src_lang]}).${languages[$src_lang]}
  pseudocode_generation $src_dataset "$src_lang" "$base_name"
done

# # Translate for evalplus dataset
# for source_lang in "${source_languages_evalplus[@]}"; do
#   for file in dataset/evalplus/$source_lang/Code/*.${languages[$source_lang]}; do
#     base_name=$(basename "$file" .${languages[$source_lang]}).${languages[$source_lang]}
#     pseudocode_generation "evalplus" "$source_lang" "$base_name"
#   done
# done

# echo "Test Generation tasks completed."
