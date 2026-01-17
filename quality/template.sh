#!/bin/bash

#SBATCH -J SONAR_##MODEL####DATASET##_##SRC_LANG##_##TGT_LANG##
#SBATCH -n 1
#SBATCH --mem=30GB
#SBATCH --gpus=0
#SBATCH --time=24:00:00
#SBATCH -o _%x%J.out
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=osdefr@gmail.com
#######-

source /etc/profile.d/modules.sh

module purge

module load java/17.0.2
module load gcc/11.5
module load go/1.24.5
module load python/3.11.6
module load cuda/12.3.2
module load cmake/4.0.0
module load anaconda/3.2024.10.1

export LD_LIBRARY_PATH=/usr/lib64:/lib64
export PATH="$HOME/my-nodejs/bin:$PATH"
export PATH="$HOME/rust/bin:$PATH"
eval "$(conda shell.bash hook)"
conda activate code_trans

export SONAR_HOME="$HOME/sonar"
export SONAR_SCANNER_HOME="$SONAR_HOME/sonar-scanner"
export BUILD_WRAPPER_HOME="$SONAR_HOME/build-wrapper"
export PATH="$SONAR_SCANNER_HOME/bin:$BUILD_WRAPPER_HOME:$PATH"
source set_token.sh
echo "SONAR_TOKEN: $SONAR_TOKEN"

bash analyse_pair.sh ##MODEL## ##DATASET## translation_source Generations ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl Generations ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl_and_source Generations ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##

bash analyse_pair.sh ##MODEL## ##DATASET## translation_source Repair ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl Repair ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl_and_source Repair ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
