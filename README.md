Pelican Server
==============
Lightweight web server application and web frontend for Pelican.

# Usage

## Pre-Requisites

* Python 3.5+
* VirtualEnv
* Pip
* miniDLNA (Fully configured)
* NPM

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

The server will be available at `localhost:8000`. The root of the server will provide a web remote for controlling the server.

## Test

### Python Backend

Testing is integrated into the launch script. If the tests fail, the server will not be launched. However, it is possible to manually run the tests from the project root directory using:
```bash
pytest
```

Most other Python testing runners are also compatible with this project in-place of `pytest`.

### React Frontend

The React frontend can be launched at `localhost:3000` in development mode from the root of this project using:

```bash
npm start
```

A production build can be triggered from the root of this project with:

```bash
npm install
npm run build
```

The production build will place static build files into `build/`.

## Monitor
Pelican Server serves Prometheus metrics at `/metrics`. As well as typical metrics provided by [Prometheus Flask Exporter](https://github.com/rycus86/prometheus_flask_exporter), custom metrics detailing the current activation state of Pelican can be found via the following gauges:

* `pelican_status_is_activated`
* `pelican_status_is_deactivated`
* `pelican_status_is_modifying`
* `pelican_status_is_scanning`

At any one time, one of these metrics will have a value of `1` (meaning true), whereas the others will have values of `0` (false).