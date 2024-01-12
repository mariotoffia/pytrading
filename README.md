# pytrading
Tests of trading strategies in Python. I use vscode, conda (miniforge) and jupyter notebooks. 

## Installation

If you want to isolate the installation, create a virtual environment first using virtualenv or conda. Then, install the dependencies using:

```bash
make dep
```

### Virtualenv environment
Create and activate the environment:

```bash
virtualenv -p python3.12 pytrading
source python/bin/activate
pip install -r requirements.txt
```

Deactivate & remove the environment:
```bash
deactivate
rm -rf pytrading
```

### Conda environment

Create and activate the environment:
```bash
conda create --name pytrading python=3.12
conda activate pytrading
pip install -r requirements.txt
```

Deactivate & remove the environment:
```bash
conda deactivate
conda env remove --name pytrading
```

#### Miniforge Conda
Since I've got a Mac M1, I use miniforge conda, installed by `brew`. It's a conda distribution for ARM64 processors.

```bash
brew install miniforge
conda init zsh
```

Restart the terminal and check the installation:

```bash
conda info
```

Another alternative is to use the official conda distribution for ARM64 processors. It's available at https://www.anaconda.com/products/individual.
