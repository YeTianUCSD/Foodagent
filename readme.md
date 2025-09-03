# FoodAgent

## Installation

### 1. Create the Conda environment
Make sure you have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed.

```bash
conda env create -f foodagent_environment.yml
```
If there are any issues with the installation of the environment, please directly refer to the [openCHA](https://github.com/Institute4FutureHealth/CHA).

### 2. Configure Conda
Add Miniconda to your PATH and initialize Conda:

```bash
echo 'export PATH="/home/foodagent/miniconda/bin:$PATH"' >> ~/.bashrc
conda init bash
source ~/.bashrc
```

### 3. Activate the environment
```bash
conda activate openCHA
```

## Running the Project

To start the main script, run:

```bash
python3 /home/foodagent/code/Agent4Health/run.py
```
---

## Notes
- Adjust the paths if your Miniconda or project directory is installed in a different location.  
- If you run into issues with Conda not being recognized, double-check that your `~/.bashrc` has been reloaded (`source ~/.bashrc`).  
- For environment reproducibility, `foodagent_environment.yml` is provided in the repo.


---

This code is modified based on [openCHA](https://github.com/Institute4FutureHealth/CHA).
