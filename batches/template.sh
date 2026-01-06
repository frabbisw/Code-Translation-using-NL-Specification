#!/bin/bash

#SBATCH -J ##DATASET##_##SRC_LANG##_##TGT_LANG##
#SBATCH -n1
#SBATCH --mem=60GB
#SBATCH --gpus=2
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

export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

eval "$(conda shell.bash hook)"
conda activate code_trans

nvidia-smi

cd ../
# python nlspec_adapter.py magicoder /home/f_rabbi/models ##DATASET## ##LANG##
python pipeline.py  --dataset ##DATASET## --source_lang ##SRC_LANG## --target_lang ##TGT_LANG## --model ##MODEL## --models_dir /home/f_rabbi/models -n -s -b

