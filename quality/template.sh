#!/bin/bash

#SBATCH -J SONAR_##MODEL####DATASET##_##SRC_LANG##_##TGT_LANG##
#SBATCH -n 1
#SBATCH --mem=30GB
#SBATCH --gpus=0
#SBATCH --time=72:00:00
#SBATCH -o _%x%J.out
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=osdefr@gmail.com
#######-

# -------------------------------
# Load environment modules
# -------------------------------
source /etc/profile.d/modules.sh

module purge

module load java/17.0.2
module load gcc/11.5
module load go/1.24.5
module load python/3.11.6
module load cuda/12.3.2
module load cmake/4.0.0
module load anaconda/3.2024.10.1

# -------------------------------
# Protect system ncurses / bash
# (prevents libtinfo.so warning)
# -------------------------------
export LD_LIBRARY_PATH=/usr/lib64:/lib64

# -------------------------------
# User-local tools
# -------------------------------
export PATH="$HOME/my-nodejs/bin:$PATH"
export PATH="$HOME/rust/bin:$PATH"

# -------------------------------
# Activate conda safely
# -------------------------------
eval "$(conda shell.bash hook)"
conda activate code_trans

# -------------------------------
# Sonar token setup
# -------------------------------
bash set_token.sh
echo "SONAR_TOKEN: $SONAR_TOKEN"

bash analyse_pair.sh ##MODEL## ##DATASET## translation_source Generations itr0 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_source Repair itr1 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_source Repair itr2 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_source Repair itr3 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##

bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl Generations itr0 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl Repair itr1 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl Repair itr2 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash analyse_pair.sh ##MODEL## ##DATASET## translation_nl Repair itr3 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##

bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Generations itr0 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Repair itr1 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Repair itr2 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##
bash quality_analysis.sh ##MODEL## ##DATASET## translation_nl_and_source Repair itr3 ##SRC_LANG## ##TGT_LANG## ##ORG_NAME##


