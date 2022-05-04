# Embedded Device

This work is for DSD2022 at JLU and UTAD. DSD represents **D**istributed **S**oftware **D**evelopment. This cycle of DSD in the spring of 2022 motivates students to design a large commercial intelligent prosthesis management system.

Team **Pigeonhole** is responsible for the code development and deployment of the embedded device controller. Our project includes two parts - cloud platform and embedded device backend.

## Introduction

This project is supported by [Flask](https://github.com/pallets/flask). The embedded device receives requests from frontend clients, and controls the model predicting. All APIs are in RESTful architecture style. It aims at a comprehensive interface for the frontend to control the device.

## Usage

Run the following command to install the dependencies:

```
git clone https://github.com/PigeonholeDSD/embedded-device.git
cd embedded-device/
pip install -r requirements.txt
git submodule update --init
pip install -r algo/requirements.txt
```

Because we use submodule to manage database and algorithm module, if there're new commits, sync and commit with:

```
git submodule update --remote --merge
git commit -am 'chroe: sync <mod>'
```

Run in the development mode:

```
python app.py
```

The default listening address would be `http://localhost:8001`.

If you would like to run in the debug mode, please pass `debug=True` to `app.run()`, i.e. `app.run(debug=True)`.

Use a production-ready WSGI server for deployment, for example:

```
gunicorn --chdir /path/to/embedded-device app:app
```

## API Documentation

To learn more about API documentation, please see [API Documentation](https://doc.ciel.pro/_nz-ppsiSa6RPzR7zwd6Bg?both).

## License

All rights reserved. If you want to use this program, please contact https://pigeonhole.fun for a private license, free of charge maybe.
