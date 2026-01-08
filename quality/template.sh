#!/bin/bash

#SBATCH -J ##MODEL####DATASET##_##SRC_LANG##_##TGT_LANG##_SONAR
#SBATCH -n1
#SBATCH --mem=30GB
#SBATCH --gpus=0
#SBATCH --time=72:00:00
#SBATCH -o _%x%J.out
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=osdefr@gmail.com
#######-

source /etc/profile.d/modules.sh

module load java/17.0.2
module load gcc/11.5
module load go/1.24.5
module load python/3.11.6
module load cuda/12.3.2
module load anaconda/3.2024.10.1

export PATH="$HOME/my-nodejs/bin:$PATH"
export PATH="$HOME/rust/bin:$PATH"
export SONAR_TOKEN=2b2da2926e0fee16fc61424a715325c5c7580b2e

eval "$(conda shell.bash hook)"
conda activate code_trans

bash analyse_pair MODEL=$1
DATASET=$2
TRANS_TYPE=$3
GEN=$4
ITR=$5
SRC_LANG=$6
TGT_LANG=$7
ORG_NAME=$8

bash quality_analysis.sh ##MODEL## ##DATASET## translation_source Generations itr0 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_source Repair itr1 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_source Repair itr2 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_source Repair itr3 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##

bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl Generations itr0 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl Repair itr1 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl Repair itr2 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl Repair itr3 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##

bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Generations itr0 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Repair itr1 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Repair itr2 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Repair itr3 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
