#!/bin/bash

#SBATCH -J generate_##DATASET##_##LANG##
#SBATCH -n4
#SBATCH --mem=30GB
#SBATCH --gpus=1
#SBATCH --time=72:00:00
#SBATCH -o _%x%J.out
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=osdefr@gmail.com

source /etc/profile.d/modules.sh

module load python/3.11.6
module load cuda/12.3.2
module load anaconda/3.2024.10.1

eval "$(conda shell.bash hook)"
conda activate code_trans
cd ../
# python nlspec_adapter.py magicoder /home/f_rabbi/models ##DATASET## ##LANG##
python pipeline_avatar_codenet.py  --dataset ##DATASET## --source_lang ##SRC_LANG## --target_lang ##TGT_LANG## --model ##MODEL## --models_dir /home/f_rabbi/models

