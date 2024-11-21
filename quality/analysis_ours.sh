#!/bin/bash

current_dir=$(pwd)

declare -A lang_map

# Populate the array with key-value pairs
lang_map["C++"]="cpp"
lang_map["Java"]="java"
lang_map["Go"]="go"
lang_map["C"]="c"
lang_map["Python"]="py"

datasets=("codenet" "avatar" "evalplus")
langs=("C++" "Java" "C" "Python" "Go")

sonar_c_cpp() {
  cd workspace || exit
  local dir=$1
  local dataset=$2
  local src=$3
  local target=$4
  local issues_dir=$5
  local organization=$6
  mkdir "Code"
  cp -r "$dir"/* "Code/"
  find Code/ -maxdepth 1 -type f \( -name '*.c' -o -name '*.cpp' \) -exec bash -c 'ext="${1##*.}"; dir="$(dirname "$1")"; base="$(basename "$1" .$ext)"; mkdir -p "$dir/$base" && mv "$1" "$dir/$base/$base.$ext"' _ {} \;
  cp ../CMakeLists.txt .
  mkdir build
  cd build || exit
  cmake "$current_dir"/workspace
  build-wrapper-linux-x86-64 --out-dir "$current_dir"/workspace/bw-output make -k
  cd .. || exit
  sonar-scanner -Dsonar.scm.disabled=true -Dsonar.organization="$organization" -Dsonar.projectKey="$organization"_"$dataset"_"$src"_"$target" -Dsonar.sources=Code -Dsonar.cfamily.compile-commands=bw-output/compile_commands.json -Dsonar.host.url=https://sonarcloud.io
  sleep 1
  cd .. || exit
  python get_info.py "$dir" "$dataset" "$src" "$target" "$issues_dir" "$organization"
  echo "Generated SONAR Report for $dir"
  rm -r workspace/*
  rm -r workspace/.scannerwork
  sleep 5
}

sonar_java() {
  cd workspace || exit
  local dir=$1
  local dataset=$2
  local src=$3
  local target=$4
  local issues_dir=$5
  local organization=$6
  mkdir "Code"
  cp -r "$dir"/* "Code/"
  find Code/ -maxdepth 1 -type f -name '*.java' -exec bash -c 'ext="${1##*.}"; dir="$(dirname "$1")"; base="$(basename "$1" .$ext)"; mkdir -p "$dir/$base" && mv "$1" "$dir/$base/$base.$ext"' _ {} \;
  find Code/ -type f -name '*.java' -exec javac {} \;
  find Code/ -type f -name "*.java" -exec bash -c 'java_file="{}"; class_file="${java_file%.java}.class"; [ ! -f "$class_file" ] && echo "Deleting $java_file" && rm "$java_file"' \;
  sonar-scanner -Dsonar.scm.disabled=true -Dsonar.organization="$organization" -Dsonar.projectKey="$organization"_"$dataset"_"$src"_"$target" -Dsonar.sources=Code -Dsonar.host.url=https://sonarcloud.io -Dsonar.java.binaries=Code
  sleep 1
  cd .. || exit
  python get_info.py "$dir" "$dataset" "$src" "$target" "$issues_dir" "$organization"
  echo "Generated SONAR Report for $dir"
  rm -r workspace/*
  rm -r workspace/.scannerwork
  sleep 5
}

sonar_go_py() {
  cd workspace || exit
  local dir=$1
  local dataset=$2
  local src=$3
  local target=$4
  local issues_dir=$5
  local organization=$6
  mkdir "Code"
  cp -r "$dir"/* "Code/"
  sonar-scanner -Dsonar.scm.disabled=true -Dsonar.organization="$organization" -Dsonar.projectKey="$organization"_"$dataset"_"$src"_"$target" -Dsonar.sources=Code -Dsonar.host.url=https://sonarcloud.io
  sleep 1
  cd .. || exit
  python get_info.py "$dir" "$dataset" "$src" "$target" "$issues_dir" "$organization"
  echo "Generated SONAR Report for $dir"
  rm -r workspace/*
  rm -r workspace/.scannerwork
  sleep 5
}


run_all() {
  root=$1
  issues_dir=$2
  organization=$3

  cnt=0
  for d in "${datasets[@]}"; do
    for src in "${langs[@]}"; do
      for target in "${langs[@]}"; do
        dir="$root/$d/$src/$target"
        if [ -d "$dir" ]; then
          cnt=$((cnt+1))
          echo "Processing: $dir" "$cnt"
          if [[ "${lang_map[$target]}" == "cpp" ]]; then
            sonar_c_cpp "$dir" "$d" "${lang_map[$src]}" "${lang_map[$target]}" "$issues_dir" "$organization"
          elif [[ "${lang_map[$target]}" == "java" ]]; then
            sonar_java "$dir" "$d" "${lang_map[$src]}" "${lang_map[$target]}" "$issues_dir" "$organization"
          elif [[ "${lang_map[$target]}" == "go" ]]; then
            sonar_go_py "$dir" "$d" "${lang_map[$src]}" "${lang_map[$target]}" "$issues_dir" "$organization"
          elif [[ "${lang_map[$target]}" == "c" ]]; then
            sonar_c_cpp "$dir" "$d" "${lang_map[$src]}" "${lang_map[$target]}" "$issues_dir" "$organization"
          elif [[ "${lang_map[$target]}" == "py" ]]; then
            sonar_go_py "$dir" "$d" "${lang_map[$src]}" "${lang_map[$target]}" "$issues_dir" "$organization"
          else
            echo "No match found for: $dir"
          fi
        fi
      done
    done
  done
  echo "$root Total directories: $cnt"
}

run_all <data_path> "outputs/repair_src_nl" "after-src-nl"
run_all <data_path> "outputs/nl_only" "before-nl-only"
run_all <data_path> "outputs/src_nl" "before-src-nl"
