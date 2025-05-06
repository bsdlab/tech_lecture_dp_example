# Strawman Module example for tech lecture

This example extends the [`strawman module`](https://github.com/bsdlab/dp-strawman-module) for [`Dareplane`](https://github.com/bsdlab/Dareplane) with a mockup example which is creating a logging output either in continuous streaming mode or just once.

## Install

The common routine: clone, install requirements and run.
Here is e.g., with using `uv` to manage the virtual environment:

```bash
git https://github.com/bsdlab/tech_lecture_dp_example
cd tech_lecture_dp_example
uv venv .venv
source .venv/bin/activate
uv sync
uv run -m api.server
```

## Connecting and communicating

Then from another terminal you can connect to the server using, e.g. `telnet` and try the primary commands:

```bash
telnet 127.0.0.1 8080
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
Connected to mymodule_control_server
GET_PCOMMS
```

The default server also implements a `STOP` command to stop any thread or subprocess which the server has in its book keeping. Additionally, a `CLOSE` command is implemented by default and will close the server. For integrating the module, the default server provides a `GET_PCOMMS` implementation, which will send the list of commands you specified + `STOP` and `CLOSE`. This is used within the control_room module (used to compose various Dareplane modules) and allows for arbitrary command name choices. You just need to reflect them properly later, when setting up the module as part of a whole system. So better choose simple and indicative names. There is not restrictions to using all capital letters either. But given the global nature of these commands, it feels natural.

Note that the communication via primary commands allows to send arbitrary json payloads. So sending `HELLO|{"n": 5}` would result in a function call of the form `run_hello_world(n= 5)`.
