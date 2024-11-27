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

## Generating NL Spec

```
./generate_nlspec.sh
```
## Generating Translations using NL spec 

```
./generate_translations.sh
```
## Generating Translations using source + NL spec

```
./generate_translation_using_source_code.sh
```

# Process of evaluation task handling Avatar and Codenet Dataset

## Evaluating Translations generated using NL spec

```
./evaluate_translation.sh translation_evaluation.py
```
## Evaluating Translations generated using source + NL spec

```
./evaluate_translation.sh translation_evaluation_using_source_code.py
```
# Process of evaluation task handling Avatar and Codenet Dataset

We built an intellije project with Maven, containing Surefire to generate unit tests report. After generating the reports file by file we run the command to generate the overall report:
```
python3 translation_evaluation_evalplus.py --source_lang "Python" --target_lang "Java" --report_dir "<directory to save report file>" --attempt 1
```

## Repairing Compilation Errors
```
python3 translation_evaluation_evalplus.py --source_lang "Python" --target_lang "Java" --report_dir "<directory to save report file>" --attempt 1
```

N.B: In some python scripts, you need to specify translation_dir variable to point the directory having the codes you want to evaluate.


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
