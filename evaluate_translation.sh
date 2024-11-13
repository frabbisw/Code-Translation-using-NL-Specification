#!/bin/bash

# Define the datasets, languages, and models
datasets=("avatar" "codenet")
source_languages_avatar=("Java" "Python")
source_languages_codenet=("C" "C++" "Go" "Python" "Java")
source_languages_evalplus=("Python")
target_languages_avatar_codenet=("C" "C++" "Go" "Python" "Java")
target_languages_evalplus=("Java")

# models=("GPT-4o-mini" "GPT-4")
models=("gpt-4o-mini")

python_script=$1

# Function to perform translation
translation_evaluation() {
  local dataset=$1
  local source_lang=$2
  local target_lang=$3

  echo "Generating evaluation report from $source_lang to $target_lang in dataset $dataset ..."
  python $python_script --dataset "$dataset" --source_lang "$source_lang" --target_lang "$target_lang"
}

# Evaluate translation for avatar dataset
for source_lang in "${source_languages_avatar[@]}"; do
  for target_lang in "${target_languages_avatar_codenet[@]}"; do
    translation_evaluation "avatar" "$source_lang" "$target_lang"
  done
done

# Evaluate translation for codenet dataset
for source_lang in "${source_languages_codenet[@]}"; do
  for target_lang in "${target_languages_avatar_codenet[@]}"; do
    translation_evaluation "codenet" "$source_lang" "$target_lang"
  done
done

# # Translate for evalplus dataset
# for source_lang in "${source_languages_codenet[@]}"; do
#   for target_lang in "${target_languages_evalplus[@]}"; do
#     for file in dataset/evalplus/$source_lang/Code/*.${languages[$source_lang]}; do
#       base_name=$(basename "$file" .${languages[$source_lang]}).${languages[$source_lang]}
#       translation_generation "evalplus" "$source_lang" "$target_lang" "$base_name"
#     done
#   done
# done

# echo "Test Generation tasks completed."