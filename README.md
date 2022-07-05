# kwalitee-dashboard-back-end

[![CircleCI](https://circleci.com/gh/OCR-D/kwalitee-dashboard-back-end/tree/main.svg?style=svg)](https://circleci.com/gh/OCR-D/kwalitee-dashboard-back-end/tree/main)

The back end of the OCR-D quality dashboard webapp.

The webapp is available over at the [OCR-D website](https://ocr-d.de/kwalitee/).

## Dependencies

- Python 3.6 or higher

## Installation

- clone the repository
- switch to the cloned directory
- execute `pip install -e .` for local installation

## Usage

The scheduled pipeline of this repo updates the `repos.json` file every night which serves as data for the webapp.

## JSON Validation

In order to validate the resulting JSON files, use

```bash
python3 schema/validation.py {FILENAME}
```

with `{FILENAME}` being either `repos.json` or `ocrd_all_releases.json`, depending on which one you'd like to validate.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](LICENSE)