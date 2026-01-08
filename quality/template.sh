#!/bin/bash

#SBATCH -J ##DATASET##_##SRC_LANG##_##TGT_LANG##_SONAR
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

eval "$(conda shell.bash hook)"
conda activate code_trans

bash quality_analysis.sh <path-to-target-codebase> <output_directory> <ORG_NAME>
python download_missings.py <output_directory> <ORG_NAME>
