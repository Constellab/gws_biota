
<p align="center">
  <img src="https://constellab.space/assets/fl-logo/constellab-logo-text-white.svg" alt="Constellab Logo" width="80%">
</p>

<br/>

# Welcome to GWS Biota 👋

```gws_biota``` is a [Constellab](https://constellab.io) library (called bricks) developped by [Gencovery](https://gencovery.com/). GWS stands for Gencovery Web Services.

## What is Constellab?

Gencovery is a software company that offers Constellab, the leading open and secure digital infrastructure designed to consolidate data and unlock its full potential in the life sciences industry. Gencovery's mission is to provide universal access to data to enhance people's health and well-being.

🌍 With our Open Access offer, you can use Constellab for free. [Sign up here](https://constellab.space/). Find more information about the Open Access offer here (link to be defined).

## Features

Biota is a unified and structured collection of omics data from official open European biological databases.
It is dedicated to Gencovery Web Services for the conception and use of digital twins of cell metabolism.

## Documentation

📄  For `gws_biota` brick documentation, click [here](https://constellab.community/bricks/gws_biota/latest/doc/getting-started/b52068ea-05cd-40c3-a6b9-68d06cffcaf4)

📄 For Constellab application documentation, click [here](https://constellab.community/bricks/gws_academy/latest/doc/getting-started/b38e4929-2e4f-469c-b47b-f9921a3d4c74)

## Installation

The `gws_biota` brick requires the `gws_core` brick.

### Recommended Method

The best way to install a brick is through the Constellab platform. With our Open Access offer, you get a free cloud data lab where you can install bricks directly.

Learn about the data lab here : [Overview](https://constellab.community/bricks/gws_academy/latest/doc/digital-lab/overview/294e86b4-ce9a-4c56-b34e-61c9a9a8260d) and [Data lab management](https://constellab.community/bricks/gws_academy/latest/doc/digital-lab/on-cloud-digital-lab-management/4ab03b1f-a96d-4d7a-a733-ad1edf4fb53c)

### Manual installation

This section is for users who want to install the brick manually. It can also be used to install the brick manually in the Constellab Codelab.

We recommend installing using Ubuntu 22.04 with python 3.10.

Required packages are listed in the ```settings.json``` file, for now the packages must be installed manually.

```bash 
pip install biopython==1.79 pronto==2.5.7 ujson==5.10.0 pyparsing==3.0.6
```

#### Usage


To start the server :

```bash
python3 manage.py --runserver
```

To run a given unit test

```bash
python3 manage.py --test [TEST_FILE_NAME]
```

Replace `[TEST_FILE_NAME]` with the name of the test file (without `.py`) in the tests folder.

To run the whole test suite, use the following command:

```bash
python3 manage.py --test all
```

VSCode users can use the predefined run configuration in `.vscode/launch.json`.

## Declare new version

To declare a new version of the DB, see prepare_db.sh script.

## Community

If you have any questions or suggestions, please feel free to contact us at gencovery@contact.com

Feel free to open an issue if you have any question or suggestion.

## License

```gws_biota``` is completely free and open-source and licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Constellab
For more information about Constellab, visit [our website](https://constellab.io).

This brick is maintained with ❤️ by [Gencovery](https://gencovery.com/).

<p align="center">
  <img src="https://framerusercontent.com/images/Z4C5QHyqu5dmwnH32UEV2DoAEEo.png?scale-down-to=512" alt="Gencovery Logo"  width="30%">
</p>