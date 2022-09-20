# quiver-dashboard-back-end

[![CircleCI](https://circleci.com/gh/OCR-D/quiver-dashboard-back-end/tree/main.svg?style=svg)](https://circleci.com/gh/OCR-D/quiver-dashboard-back-end/tree/main)

The back end of the OCR-D quality dashboard webapp.

The webapp is available over at the [OCR-D website](https://ocr-d.de/quiver/).

## Dependencies

- Python 3.6 or higher

## Installation

- clone the repository
- switch to the cloned directory
- execute `pip install -e .` for local installation

## Usage

The scheduled pipeline of this repo updates the `data/repos.json` file every night which serves as data for the webapp.

For local usage, execute `make repos.json`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](LICENSE)