#!/bin/bash

# Define the datasets, languages, and models
datasets=("avatar" "codenet" "evalplus")
source_languages_avatar=("Java" "Python")
source_languages_codenet=("C" "C++" "Go" "Python" "Java")
source_languages_evalplus=("Python")
target_languages=("C" "C++" "Go" "Python" "Java")


# Function to perform translation
translate() {
  local dataset=$1
  local source_lang=$2
  local target_lang=$3

  if [ "$source_lang" != "$target_lang" ]; then
    echo "Debugging from $source_lang to $target_lang in dataset $dataset using model $model..."
    python compilation_errors_fixation.py --dataset "$dataset" --source_lang "$source_lang" --target_lang "$target_lang" --translation_dir "repair/debug_on_translated_codes_itr1" #"translation/base_translation"
  fi
}

# Translate for avatar dataset
for source_lang in "${source_languages_avatar[@]}"; do
  for target_lang in "${target_languages[@]}"; do
    translate "avatar" "$source_lang" "$target_lang"
  done
done

# Translate for codenet dataset
for source_lang in "${source_languages_codenet[@]}"; do
  for target_lang in "${target_languages[@]}"; do
    translate "codenet" "$source_lang" "$target_lang"
  done
done

# # Translate for avatar dataset
# for source_lang in "${source_languages_evalplus[@]}"; do
#   for target_lang in "${target_languages[@]}"; do
#     translate "evalplus" "$source_lang" "$target_lang"
#   done
# done

echo "Debug tasks completed."