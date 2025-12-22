#!/bin/bash

# Define the datasets, languages, and models
datasets=("avatar" "codenet" "evalplus")
source_languages_avatar=("Java" "Python")
source_languages_codenet=("C" "C++" "Go" "Python" "Java")
source_languages_evalplus=("Python")
target_languages=("C" "C++" "Go" "Python" "Java")

source_languages_codenet=("C++")
target_languages=("C")

translation_dir=$1 # "repair/debug_on_translated_codes_base"
report_dir=$2
output_dir=$3 # "repair/debug_on_translated_codes_itr1"
model=$4
model_dir=$5

# Function to perform translation
debug() {
  local dataset=$1
  local source_lang=$2
  local target_lang=$3

  if [ "$source_lang" != "$target_lang" ]; then
    echo "Debugging from $source_lang to $target_lang in dataset $dataset using model $model..."
    python all_errors_fixation.py --dataset "$dataset" --source_lang "$source_lang" --target_lang "$target_lang" --translation_dir "$translation_dir" --report_dir "$report_dir" --out_dir "$output_dir" --model "$model" --models_dir "$model_dir"
  fi
}

# # debug for avatar dataset
# for source_lang in "${source_languages_avatar[@]}"; do
#   for target_lang in "${target_languages[@]}"; do
#     debug "avatar" "$source_lang" "$target_lang"
#   done
# done

# # debug for codenet dataset
# for source_lang in "${source_languages_codenet[@]}"; do
#   for target_lang in "${target_languages[@]}"; do
#     debug "codenet" "$source_lang" "$target_lang"
#   done
# done

# debug for codenet(InterTrans) dataset
for source_lang in "${source_languages_codenet[@]}"; do
  for target_lang in "${target_languages[@]}"; do
    debug "codenetintertrans" "$source_lang" "$target_lang"
  done
done

# # debug for evalplus dataset
# for source_lang in "${source_languages_evalplus[@]}"; do
#   for target_lang in "${target_languages[@]}"; do
#     debug "evalplus" "$source_lang" "$target_lang"
#   done
# done

echo "Debug tasks completed."