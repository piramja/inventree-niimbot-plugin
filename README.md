[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PEP](https://github.com/inventree/inventree-python/actions/workflows/pep.yaml/badge.svg)


# inventree-niimbot-plugin

A label printing plugin for [InvenTree](https://inventree.org), which provides support for the [Niimbot Label Printers](https://www.niimbot.com/enweb/product_label.html?category_id=6). This plugin is based on the amazing work from [labbots/NiimPrintX](https://github.com/labbots/NiimPrintX/tree/main) and modifications from [LorisPolenz/NiimPrintX](https://github.com/LorisPolenz/NiimPrintX/tree/main).

## Installation

Install this plugin manually as follows:

```
pip install inventree-niimbot-plugin
```

Or, add to your `plugins.txt` file to install automatically using the `invoke install` command:

```
inventree-niimbot-plugin
```

## Configuration Options
The following list gives an overview of the available settings. You find them under the InvenTree plugin specific settings.

* **Printer Model**
Currently supported models are: 
b1, b18, b21, d11, d110 (but i was only able to test b1 because i don't have other printer models. Please report back if you can test other models!!).

* **Density**
The print density. Different models seem to accept only certain values (b1 accepts 1-3).

* **Rotation**
Rotation angle, either 0, 90, 180 or 270 degrees.

* **Scaling**
Scaling factor, from 10% to 200%.

* **Vertical Offset**
Vertical offset, from 0 to 200px.

* **Horizontal Offset**
Horizontal offset, from 0 to 200px.


## Usage

Once installed, the plugin should show up under **Settings -> Plugin Settings -> Plugins** and be activated.

You can then adjust the printer settings under **Settings -> Plugin Settings -> Niimbot Label Printer**.

As a starting point, you can use my settings for the B1 printer with 50x30mm standard labels and the "InvenTree Part Label" template:

**Printer Model**: Niimbot B1,
**Density**: 3,
**Rotation**: 270°,
**Scaling**: 60%,
**Vertical Offset**: 50px,
**Horizontal Offset**: 0px

You can either connect the printer via USB or bluetooth. When using bluetooth, you need to pair the printer with the machine running InvenTree (e.g using bluez-tools on terminal). The printer is then detected automatically.

## Known Issues

The plugin system seemed to be broken in recent InvenTree docker images. I was not able to install the plugin without errors. Furthermore, i am not sure if it's even possible to access bluetooth or USB devices from within a docker image.

I therefore was only able to use the plugin with bare metal installation of InvenTree. The bare metal installation also fixed many other issues the docker image had and worked like a charm, although it takes a little extra effort.
