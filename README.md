# quiver-dashboard-back-end

[![CircleCI](https://circleci.com/gh/OCR-D/quiver-back-end/tree/main.svg?style=svg)](https://circleci.com/gh/OCR-D/quiver-back-end/tree/main)

The back end of the OCR-D quality dashboard webapp.

The webapp is available over at the [OCR-D website](https://ocr-d.de/quiver-frontend/).

## Dependencies

- Python 3.6 or higher

## Installation

- clone the repository
- switch to the cloned directory
- execute `pip install -e .` for local installation

## Usage

The scheduled pipeline of this repo updates the `data/repos.json` file every night which serves as data for the webapp.

For local usage, execute `make repos.json`.

## Adding New Workflows

New workflows can be added as TXT files in the `workflows/ocrd_workflows` directory.

Files either have to end with `eval.txt` (if they contain an evaluation workflow) or `ocr.txt` (if they contain an OCR workflow).
The file names have to stick to snake case.


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](LICENSE)
