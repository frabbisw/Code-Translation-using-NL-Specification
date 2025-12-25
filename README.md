# Specification-Driven Code Translation By Large Language Models: How Far Are We?

## Installation and Setup
We have used python3.10 for our whole experiment. install the necessary pip packages by running `pip install -r requirements.txt`

The Datasets and Artifacts are available [here](https://zenodo.org/records/14194996?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImQ0MGI4NWFkLTE3ZTEtNDQ1Ny05ZTJhLTBlYTgzYTdjMTQyNSIsImRhdGEiOnt9LCJyYW5kb20iOiI2ZDc1YmU1ZmZkNGU0YTUxMmU2MWFjOTQ2MTU1NmQ1ZSJ9.AHT4Y1VtQoDiTQB0bikyot2gFC8NuYjnBS3O1R3F8u_YvM2pWa5c_uqMnIjAdaMsqKXcaOgaZ4mxLjpAa5wbHQ).

## Structure of the database

The structure of the dataset should to be as follows:
```
dataset
├─ avatar
│   ├─ Python
│   │   ├─ Code
│   │   │   ├─ XYZ.py
│   │   │   └─ ...
│   │   ├─ TestCases
│   │   └─  ├─ XYZ_0.in
│   │   │   ├─ XYZ_0.out
│   │   │   ├─ XYZ_1.out
│   │   │   ├─ XYZ_2.out
│   │   │   └─ ...
│   ├─ Java
│   └─ ...
├─ codenet
└─ ...
```

## Run Pipeline For Avatar, CodeNet and CodenetIntertrans
```
python pipeline_avatar_codenet.py  --dataset dataset --source_lang source --target_lang target --model model --models_dir models_dir
# model and models_dir are optional, default model is gpt-4o-mini
```


## Run Quality Analysis
We have used SonarQube to assess the quality analysis of the generated code. To run it, we created organizations in [sonarcloud](https://sonarcloud.io/) for each set(translated with/without NL-Specs and before/after fixing the compilation errors). An API key from sonarcloud needs to be fetched and saved to $SONAR_TOKEN

To analyze the codebase, run
```
cd quality
bash quality_analysis.sh <path-to-target-codebase> <output_directory> <ORG_NAME>
```
The structure of the target codebase needs to be as follows:
```
codebase
├─ codenet <dataset>
│   ├─ Python <Src_Lang>
│   │   ├─ Java <Target_Lang>
│   │   │   ├─ XYZ.java
│   │   │   └─ ...
│   │   ├─ C++
│   │   └─ ...
│   ├─ Java
│   └─ ...
├─ avatar
└─ ...
```
After running this command, the JSON files containing the assessment will be stored in the output directory.
Due to API latency, some files can be missed from the sonarcloud. the missing files can be downloaded by following
```
cd quality
python download_missings.py <output_directory> <ORG_NAME>
```
