#!/bin/bash

current_dir=$(pwd)
project_dir=$(dirname "$current_dir")

# 1. Declare the associative array
declare -A lang_map

lang_map["C++"]="cpp"
lang_map["Java"]="java"
lang_map["Go"]="go"
lang_map["C"]="c"
lang_map["Python"]="py"
lang_map["Javascript"]="js"
lang_map["Rust"]="rs"

# 2. Assign positional arguments
MODEL=$1
DATASET=$2
TRANS_TYPE=$3
GEN=$4
ITR=$5
SRC_LANG=$6
TGT_LANG=$7
ORG_NAME=$8

# 3. Construct PROJECT_KEY using ${lang_map[$VAR]}
# In Bash, variables are concatenated just by placing them next to each other.
PROJECT_KEY="${ORG_NAME}_${MODEL}_${DATASET}_${lang_map[$SRC_LANG]}_${lang_map[$TGT_LANG]}_${TRANS_TYPE}_${GEN}_${ITR}"

if [[ "$GEN" == "Generations" ]]; then
  DATA_PATH="${project_dir}/Generations/${MODEL}/${TRANS_TYPE}/${DATASET}/${SRC_LANG}/${TGT_LANG}"
elif [[ "$GEN" == "Repair" ]]; then
  DATA_PATH="${project_dir}/Repair/${MODEL}/${TRANS_TYPE}/${ITR}/${DATASET}/${SRC_LANG}/${TGT_LANG}"
fi

# 5. Define output path
OUT_PATH="${project_dir}/sonar_report/${PROJECT_KEY}"

# Example of how to use the variables (verification)
echo "Project Key: $PROJECT_KEY"
echo "Data Path: $DATA_PATH"

sonar_c_cpp() {
  local src_dir=$1
  local tgt_path=$2
  local organization=$3
  local project_key=$4

  local workspace_dir="workspace_${project_key}"
  mkdir -p "$workspace_dir"
  cd "$workspace_dir" || return 1 
  
  mkdir "Code"
  cp -r "$src_dir"/* "Code/"
  find Code/ -maxdepth 1 -type f \( -name '*.c' -o -name '*.cpp' \) -exec bash -c 'ext="${1##*.}"; dir="$(dirname "$1")"; base="$(basename "$1" .$ext)"; mkdir -p "$dir/$base" && mv "$1" "$dir/$base/$base.$ext"' _ {} \;
  cp ../CMakeLists.txt .
  mkdir build
  cd build || return 1
  cmake "$current_dir"/"$workspace_dir"
  build-wrapper-linux-x86-64 --out-dir "$current_dir"/"$workspace_dir"/bw-output make -k
  cd .. || return 1
  sonar-scanner -Dsonar.scm.disabled=true -Dsonar.organization="$organization" -Dsonar.projectKey="$project_key" -Dsonar.sources=Code -Dsonar.cfamily.compile-commands=bw-output/compile_commands.json -Dsonar.host.url=https://sonarcloud.io
  sleep 1
  cd .. || return 1
  python get_info.py "$src_dir" "$tgt_path" "$organization" "$project_key"
  echo "Generated SONAR Report for $src_dir"
  rm -r "$workspace_dir"
  sleep 5
}

sonar_java() {
  local src_dir=$1
  local tgt_path=$2
  local organization=$3
  local project_key=$4

  local workspace_dir="workspace_${project_key}"
  mkdir -p "$workspace_dir"
  cd "$workspace_dir" || return 1 
  
  mkdir "Code"
  cp -r "$src_dir"/* "Code/"
  find Code/ -maxdepth 1 -type f -name '*.java' -exec bash -c 'ext="${1##*.}"; dir="$(dirname "$1")"; base="$(basename "$1" .$ext)"; mkdir -p "$dir/$base" && mv "$1" "$dir/$base/$base.$ext"' _ {} \;
  find Code/ -type f -name '*.java' -exec javac {} \;
  find Code/ -type f -name "*.java" -exec bash -c 'java_file="{}"; class_file="${java_file%.java}.class"; [ ! -f "$class_file" ] && echo "Deleting $java_file" && rm "$java_file"' \;
  sonar-scanner -Dsonar.scm.disabled=true -Dsonar.organization="$organization" -Dsonar.projectKey="$project_key" -Dsonar.sources=Code -Dsonar.host.url=https://sonarcloud.io -Dsonar.java.binaries=Code
  sleep 1
  cd .. || return 1
  python get_info.py "$src_dir" "$tgt_path" "$organization" "$project_key"
  echo "Generated SONAR Report for $src_dir"
  rm -r "$workspace_dir"
  sleep 5
}

sonar_script() {
  local src_dir=$1
  local tgt_path=$2
  local organization=$3
  local project_key=$4

  local workspace_dir="workspace_${project_key}"
  mkdir -p "$workspace_dir"
  cd "$workspace_dir" || return 1 
  
  mkdir "Code"
  cp -r "$src_dir"/* "Code/"
  sonar-scanner -Dsonar.scm.disabled=true -Dsonar.organization="$organization" -Dsonar.projectKey="$project_key" -Dsonar.sources=Code -Dsonar.host.url=https://sonarcloud.io
  sleep 1
  cd .. || return 1
  python get_info.py "$src_dir" "$tgt_path" "$organization" "$project_key"
  echo "Generated SONAR Report for $src_dir"
  rm -rf "$workspace_dir"
  sleep 5
}

echo "==== SonarQube environment ===="
echo "SONAR_HOME           = $SONAR_HOME"
echo "SONAR_SCANNER_HOME   = $SONAR_SCANNER_HOME"
echo "BUILD_WRAPPER_HOME   = $BUILD_WRAPPER_HOME"
echo "PATH                 = $PATH"
echo "=============================="
echo "Analyzing with SonarQube"
echo "$DATA_PATH"
echo "=============================="

# Dispatch based on TGT_LANG
if [[ "$TGT_LANG" == "C" || "$TGT_LANG" == "C++" ]]; then
    sonar_c_cpp "$DATA_PATH" "$OUT_PATH" "$ORG_NAME" "$PROJECT_KEY"
elif [[ "$TGT_LANG" == "Java" ]]; then
    sonar_java "$DATA_PATH" "$OUT_PATH" "$ORG_NAME" "$PROJECT_KEY"
else
    sonar_script "$DATA_PATH" "$OUT_PATH" "$ORG_NAME" "$PROJECT_KEY"
fi

echo "waiting for 5 sec ..."
sleep 5
python download_missings.py "$DATA_PATH" "$OUT_PATH" "$ORG_NAME" "$PROJECT_KEY"
