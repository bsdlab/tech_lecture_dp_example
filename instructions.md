# Dareplane Example Setup

This repository guides you through an example setup for the Dareplane platform.

You will learn:

- How to build a simple paradigm presenting a visual cue and recording keyboard press reactions
- Wrapping this paradigm code into a Dareplane module
- Integrating the module into a full Dareplane setup using the [Dareplane control room (`dp-control-room`)](https://github.com/bsdlab/dp-control-room)

---

## Part 1: Environment Setup

Start by cloning this repository.

```bash
git clone git@github.com:bsdlab/tech_lecture_dp_example.git
cd tech_lecture_dp_example
```

Next, create a python environment and install the required dependencies. You can use `conda`, `venv`, `uv` or any other way for managing virtual python environments.

#### Option A: Using uv 
```bash
uv venv .venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

#### Option B: Using conda
```bash
conda create -n dareplane_example python=3.13
conda activate dareplane_example 
pip install -e .
```

#### Option C: Using venv
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Verify Installation

```bash
python -c "from dareplane_utils.default_server.server import DefaultServer; print('✓ dareplane-utils installed')"
python -c "import pyglet; print('✓ pyglet installed')"
python -c "import pylsl; print('✓ pylsl installed')"
```

---

## Part 2: Understanding Dareplane Architecture

Dareplane follows a modular architecture where each component runs as an independent **module** that communicates via TCP sockets using **Primary Commands (PCOMMs)**.

```
┌─────────────────────────────────────────────────────────────────┐
│                      dp-control-room                            │
│                    (Web UI + Orchestration)                     │
└─────────────────┬───────────────┬───────────────┬───────────────┘
                  │ TCP           │ TCP           │ TCP
                  ▼               ▼               ▼
         ┌────────────┐   ┌────────────┐   ┌────────────┐
         │dp-myparadigm│   │dp-mockup-  │   │dp-lsl-     │
         │ (Port 8084)│   │ streamer   │   │ recording  │
         │            │   │ (Port 8083)│   │ (Port 8082)│
         └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
               │                │                │
               ▼                ▼                ▼
            [LSL Marker]    [LSL EEG]      [Records all
             Stream          Stream         LSL streams]
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Module** | Independent process with a TCP server responding to commands |
| **PCOMM** | Primary Command - text-based command sent via TCP (e.g., `RUN`, `STOP`) |
| **LSL** | Lab Streaming Layer - protocol for streaming time-series data |
| **Control Room** | Central orchestration module providing a web UI |

---

## Part 3: Building the Paradigm Core Logic

We'll create a simple reaction time paradigm that:
1. Shows a fixation cross
2. After a random delay (1-3s), displays a green cue
3. Records the participant's key press reaction time
4. Sends markers to an LSL stream

### 3.1 Examine the Paradigm Structure

The paradigm code is already provided in `mock_setup/dp-myparadigm/`. Let's understand its structure:

```
mock_setup/dp-myparadigm/
├── pyproject.toml          # Module dependencies
├── README.md               # Module documentation
├── myparadigm/
│   └── paradigm.py         # Core paradigm logic
└── api/
    └── server.py           # Dareplane server wrapper
```

### 3.2 Understanding the Core Paradigm

Open `mock_setup/dp-myparadigm/myparadigm/paradigm.py` and examine the key components:

```python
# The paradigm uses a state machine with these states:
# "idle" -> "fixation" -> "cue" -> "response" -> (next trial)
```

**Key methods to understand:**

| Method | Purpose |
|--------|---------|
| `_setup_lsl()` | Creates an LSL marker stream outlet |
| `_send_marker()` | Sends timestamped markers (e.g., `"cue_onset,trial=0"`) |
| `_start_trial()` | Begins a trial with fixation cross |
| `_show_cue()` | Displays the green cue and records onset time |
| `_on_key_press()` | Handles participant response, calculates RT |
| `run()` | Main entry point to start the paradigm |

### 3.3 Test the Paradigm Standalone

Before integrating with Dareplane, test the paradigm directly:

```bash
cd mock_setup/dp-myparadigm
python -m myparadigm.paradigm
```

A window should appear. Wait for the green circle, then press `SPACE`. Press `ESC` to quit early.

> **Checkpoint ✓** You should see a pyglet window cycling through fixation → cue → feedback.

---

## Part 4: Wrapping as a Dareplane Module

Now we'll wrap the paradigm in a Dareplane-compatible server.

### 4.1 Understanding the Server Wrapper

Open `mock_setup/dp-myparadigm/api/server.py`:

```python
from dareplane_utils.default_server.server import DefaultServer

# The key is mapping PCOMMs to functions:
pcomm_map = {
    "RUN": paradigm.run,      # RUN command triggers paradigm.run()
    "STOP": paradigm.stop,    # STOP command triggers paradigm.stop()
}

# Create server on specified port
server = DefaultServer(
    port=pcomm_port,
    pcomm_map=pcomm_map,
    name="dp-myparadigm",
)
```

### 4.2 Test the Server Locally

Start the module server:

```bash
cd mock_setup/dp-myparadigm
python -m api.server --pcomm_port=8084
```

In a **new terminal**, connect via telnet to test commands:

```bash
telnet 127.0.0.1 8084
```

Try these commands:
```
GET_PCOMMS
RUN|{"n_trials": 3}
```

> **Checkpoint ✓** The server should respond with available commands, and `RUN` should start the paradigm window.

---

## Part 5: Setting Up the Full Dareplane Environment

### 5.1 Download Supporting Modules

Run the setup script to clone the required Dareplane modules:

```bash
cd /path/to/tech_lecture_dp_example
python scripts/mock_setup_script.py
```

This creates:

| Module | Purpose |
|--------|---------|
| `dp-control-room` | Web-based orchestration UI |
| `dp-mockup-streamer` | Simulates EEG data stream via LSL |
| `dp-lsl-recording` | Records all LSL streams to disk |
| `dp-myparadigm` | Your paradigm module (already exists) |

### 5.2 Install Each Module

```bash
# Install control room
cd mock_setup/dp-control-room
pip install -e .

# Install LSL recording
cd ../dp-lsl-recording
pip install -e .

# Install mockup streamer
cd ../dp-mockup-streamer
pip install -e .

# Install your paradigm (if not already)
cd ../dp-myparadigm
pip install -e .
```

### 5.3 Understand the Control Room Configuration

The setup script generated a config at `mock_setup/dp-control-room/configs/cvep_speller.toml`.

Key sections:

```toml
[python.modules.dp-myparadigm]
    type = 'paradigm'
    port = 8084
    ip = '127.0.0.1'

[macros.run_paradigm]
    name = 'RUN PARADIGM'
    description = 'Start the visual cue paradigm with recording'
[macros.run_paradigm.cmds]
    com1 = ['dp-lsl-recording', 'UPDATE']
    com2 = ['dp-lsl-recording', 'SELECT_ALL']
    com3 = ['dp-lsl-recording', 'SET_SAVE_PATH', ...]
    com4 = ['dp-lsl-recording', 'RECORD']
    com5 = ['dp-myparadigm', 'RUN', 'n_trials=n_trials']
```

**Macros** chain multiple PCOMMs together - clicking "RUN PARADIGM" will:
1. Update available LSL streams
2. Select all streams for recording
3. Set the save path
4. Start recording
5. Start your paradigm

---

## Part 6: Running the Full Setup

You'll need **4 terminal windows** (or use a terminal multiplexer like `tmux`).

### Terminal 1: Start the Mockup Streamer
```bash
cd mock_setup/dp-mockup-streamer
python -m mockup_streamer.main --pcomm_port=8083
```

### Terminal 2: Start the LSL Recorder
```bash
cd mock_setup/dp-lsl-recording
python -m lsl_recording.main --pcomm_port=8082
```

### Terminal 3: Start Your Paradigm Module
```bash
cd mock_setup/dp-myparadigm
python -m api.server --pcomm_port=8084
```

### Terminal 4: Start the Control Room
```bash
cd mock_setup/dp-control-room
python -m control_room.main --setup_cfg_path=configs/cvep_speller.toml
```

### Using the Control Room

1. Open your browser to `http://127.0.0.1:8050`
2. You should see all modules connected (green status)
3. Click **"RUN PARADIGM"** macro to:
   - Start LSL recording
   - Launch the paradigm window
4. Complete the trials
5. Click **"STOP PARADIGM"** to stop recording

### Verify Recording

Check the `mock_setup/data/` folder for recorded XDF files:

```bash
ls mock_setup/data/
```

You can load and inspect XDF files with `pyxdf`:

```python
import pyxdf
data, header = pyxdf.load_xdf('mock_setup/data/sub-P001_ses-S001_run-001_task-paradigm.xdf')
for stream in data:
    print(f"Stream: {stream['info']['name'][0]}, samples: {len(stream['time_stamps'])}")
```

---

## Part 7: Creating Your Own Module (Exercise)

Now that you understand the architecture, try creating your own module:

1. **Copy the template:**
   ```bash
   cp -r mock_setup/dp-myparadigm mock_setup/dp-mymodule
   ```

2. **Modify the paradigm logic** in `myparadigm/paradigm.py`

3. **Update PCOMMs** in `api/server.py` to expose your new functionality

4. **Add to control room config** in `cvep_speller.toml`:
   ```toml
   [python.modules.dp-mymodule]
       type = 'custom'
       port = 8085
       ip = '127.0.0.1'
   ```

5. **Create macros** to integrate with other modules

---

## A Real Example

A full example of a real cVEP (code-modulated Visual Evoked Potential) speller setup can be found [here](https://github.com/thijor/dp-cvep/tree/main).

This demonstrates:
- Complex paradigm with visual stimulation
- Real-time signal processing
- Online classification and feedback
- Multi-module coordination

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not connecting | Check port numbers match config |
| LSL stream not found | Ensure mockup streamer is running first |
| Pyglet window not appearing | Check display/GPU drivers |
| Permission denied on ports | Use ports > 1024 or run with elevated privileges |

## Resources

- [Dareplane Documentation](https://github.com/bsdlab/Dareplane)
- [dareplane-utils](https://github.com/bsdlab/dareplane-utils)
- [Lab Streaming Layer](https://labstreaminglayer.org/)
- [Pyglet Documentation](https://pyglet.readthedocs.io/)
