# Dareplane example setup

This repository guides you through an example setup for the Dareplane platform.

You will learn:

- How to build a simple paradigm presenting a visual queue and recording a keyboard press reactions
- Wrapping this paradigm code into a Dareplane module
- Integrating the module into a full Dareplane setup using the [Dareplane control room (`dp-control-room`)](https://github.com/bsdlab/dp-control-room)



## Setup for the introduction

Start by cloning this repository.

```bash
git clone git@github.com:bsdlab/tech_lecture_dp_example.git
```

Next, create a python environment and install the required dependencies. You can use `conda`, `venv`, `uv` or any other way for managing virtual python environments. Below are the instructions for both Unix (bash) and Windows (PowerShell) environments.

##### Conda
```bash
conda create -n dareplane_example python=3.13
conda activate dareplane_example 
pip install -r requirements.txt
```
##### Venv
```bash
python -m venv dareplane_example
source dareplane_example/bin/activate  # On Windows use: dareplane_example\Scripts\
pip install -r requirements.txt
```

##### uv
```bash
uv env create --python 3.13
uv install -r requirements.txt
```


### Downloading the example modules
Use the Python script `./scripts/mock_setup_script.py` to download the example modules for this setup.

The setup script will create the following modules:


| Module | Purpose|
| -------------- | --------------- |
| dp-myparadigm | plain example paradigm module to showcase use interaction via keyboard presses |
| dp-mockup-streamer | data mockup streaming using [`mne-lsl`](https://mne.tools/mne-lsl/stable/index.html) |
| dp-lsl-recording | recording streaming [lsl](https://labstreaminglayer.org/#/) data |
| dp-control-room |  central orchestration module to provide a web based UI |


## Coding the paradigm

We will use 


## A real example
A full example of a real cVEP speller setup can be found [here](https://github.com/thijor/dp-cvep/tree/main).
