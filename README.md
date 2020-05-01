# Pelican Server
Lightweight web server application for Pelican.

# Usage

## Pre-Requisites

* Python 3.5+
* VirtualEnv
* Pip
* miniDLNA (Fully configured)

Project dependencies will be automatically downloaded when using the launch script.

## Launch

Define the partitions that are required by miniDLNA in `config/devices.json`. It should look similar to this:
```json
[
  {
    "path": "/dev/sda",
    "partitions": [
      {
        "path": "/dev/sda2",
        "mountPoint": "/media/pi/WD_5TB_Media"
      }
    ]
  }
]
```

From the root of the project, launch with:

```bash
./launch.sh
```

The server will be available at `localhost:8000`.