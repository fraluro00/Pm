# Scripts

Start and stop scripts for the Docker container. All scripts build the image from the project root Dockerfile and run it as `pm-app` on port 8000.

## Files

| File | Platform | Action |
|---|---|---|
| `start.sh` | Mac / Linux | Build image, stop any existing container, start new one |
| `stop.sh` | Mac / Linux | Stop and remove the container |
| `start.bat` | Windows | Build image, stop any existing container, start new one |
| `stop.bat` | Windows | Stop and remove the container |

## Usage

```bash
# Mac/Linux
./scripts/start.sh
./scripts/stop.sh
```

The start script passes `.env` from the project root into the container via `--env-file`.
