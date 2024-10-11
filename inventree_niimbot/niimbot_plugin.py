"""Niimbot label printing plugin for InvenTree.

Supports direct printing of labels to USB or Bluetooth label printers, using NiimbotPrintX.
"""

# translation
from django.utils.translation import gettext_lazy as _

# printing options
from rest_framework import serializers

from inventree_niimbot.version import NIIMBOT_PLUGIN_VERSION

# InvenTree plugin libs
from plugin import InvenTreePlugin
from plugin.mixins import LabelPrintingMixin, SettingsMixin

# Image library
from PIL import Image

import asyncio
from bleak import BleakClient, BleakScanner

# NiimbotPrintX printer client
from inventree_niimbot.nimmy.bluetooth import find_device
from inventree_niimbot.nimmy.printer import PrinterClient, InfoEnum
from inventree_niimbot.nimmy.logger_config import setup_logger, get_logger, logger_enable



class NiimbotLabelSerializer(serializers.Serializer):
    """Custom serializer class for NiimbotLabelPlugin.

    Used to specify printing parameters at runtime
    """

    copies = serializers.IntegerField(
        default=1,
        label=_('Copies'),
        help_text=_('Number of copies to print'),
    )


class NiimbotLabelPlugin(LabelPrintingMixin, SettingsMixin, InvenTreePlugin):

    AUTHOR = "piramja"
    DESCRIPTION = "Label printing plugin for Niimbot label printers"
    VERSION = NIIMBOT_PLUGIN_VERSION

    NAME = "Niimbot Labels"
    SLUG = "niimbot"
    TITLE = "Niimbot Label Printer"

    PrintingOptionsSerializer = NiimbotLabelSerializer

    # Use background printing
    BLOCKING_PRINT = False
    
    SETTINGS = {
        'MODEL': {
            'name': _('Printer Model'),
            'description': _('Select model of Niimbot printer'),
            'choices': [
                ('b1', 'Niimbot B1'),
                ('b18', 'Niimbot B18'),
                ('b21', 'Niimbot B21'),
                ('d11', 'Niimbot D11'),
                ('d110', 'Niimbot D110')
            ],
            'default': 'b1',
        },
        'DENSITY': {
            'name': _('Density'),
            'description': _('Density of the print (3 is max for b18, d11, d110)'),
            'choices': [
                ('1', 'density 1'),
                ('2', 'density 2'),
                ('3', 'density 3'),
                ('4', 'density 4'),
                ('5', 'density 5'),
            ],
            'default': '3',
        },
        'ROTATION': {
            'name': _('Rotation'),
            'description': _('Image rotation (clockwise)'),
            'choices': [
                ('0', '0 degrees'),
                ('90', '90 degrees'),
                ('180', '180 degrees'),
                ('270', '270 degrees'),
            ],
            'default': '0',
        },
        'SCALING': {
            'name': _('Scaling (%)'),
            'description': _('Image scaling in percent'),
            'choices': [
                ('2', '200%'),
                ('1.9', '190%'),
                ('1.8', '180%'),
                ('1.7', '170%'),
                ('1.6', '160%'),
                ('1.5', '150%'),
                ('1.4', '140%'),
                ('1.3', '130%'),
                ('1.2', '120%'),
                ('1.1', '110%'),
                ('1', '100%'),
                ('0.9', '90%'),
                ('0.8', '80%'),
                ('0.7', '70%'),
                ('0.6', '60%'),
                ('0.5', '50%'),
                ('0.4', '40%'),
                ('0.3', '30%'),
                ('0.2', '20%'),
                ('0.1', '10%'),
            ],
            'default': '1',
        },
        'V_OFFSET': {
            'name': _('Vertical Offset (px)'),
            'description': _('Image offset vertical'),
            'choices': [
                ('0', '0px'),
                ('10', '10px'),
                ('20', '20px'),
                ('30', '30px'),
                ('40', '40px'),
                ('50', '50px'),
                ('60', '60px'),
                ('70', '70px'),
                ('80', '80px'),
                ('90', '90px'),
                ('100', '100px'),
                ('110', '110px'),
                ('120', '120px'),
                ('130', '130px'),
                ('140', '140px'),
                ('150', '150px'),
                ('160', '160px'),
                ('170', '170px'),
                ('180', '180px'),
                ('190', '190px'),
                ('200', '200px'),
            ],
            'default': '0',
        },
        'H_OFFSET': {
            'name': _('Horizontal Offset (px)'),
            'description': _('Image offset horizontal'),
            'choices': [
                ('0', '0px'),
                ('10', '10px'),
                ('20', '20px'),
                ('30', '30px'),
                ('40', '40px'),
                ('50', '50px'),
                ('60', '60px'),
                ('70', '70px'),
                ('80', '80px'),
                ('90', '90px'),
                ('100', '100px'),
                ('110', '110px'),
                ('120', '120px'),
                ('130', '130px'),
                ('140', '140px'),
                ('150', '150px'),
                ('160', '160px'),
                ('170', '170px'),
                ('180', '180px'),
                ('190', '190px'),
                ('200', '200px'),
            ],
            'default': '0',
        },
    }
    
    
    def print_label(self, **kwargs):
        """
        Send the label to the printer
        """

        # TODO: Add padding around the provided image, otherwise the label does not print correctly
        # ^ Why? The wording in the underlying brother_ql library ('dots_printable') seems to suggest
        # at least that area is fully printable.
        # TODO: Improve label auto-scaling based on provided width and height information

        # Extract width (x) and height (y) information
        # width = kwargs['width']
        # height = kwargs['height']
        # ^ currently this width and height are those of the label template (before conversion to PDF
        # and PNG) and are of little use

        # Printing options requires a modern-ish InvenTree backend,
        # which supports the 'printing_options' keyword argument
        options = kwargs.get('printing_options', {})
        n_copies = int(options.get('copies', 1))

        # Look for png data in kwargs (if provided)
        label_image = kwargs.get('png_file', None)

        if not label_image:
            # Convert PDF to PNG
            pdf_data = kwargs['pdf_data']
            label_image = self.render_to_png(label=None, pdf_data=pdf_data)
        

        # Read settings
        model = self.get_setting('MODEL')
        density = int(self.get_setting('DENSITY'))
        vertical_offset = int(self.get_setting('V_OFFSET'))
        horizontal_offset = int(self.get_setting('H_OFFSET'))
        scaling = float(self.get_setting('SCALING'))
        rotation = int(self.get_setting('ROTATION')) + 90
        rotation = rotation % 360

        # Rotate image
        if rotation in [90, 180, 270]:
            label_image = label_image.rotate(rotation, expand=True)
        
        # Resize image
        width, height = label_image.size
        new_size = (int(width * scaling), int(height * scaling))
        label_image = label_image.resize(new_size, Image.LANCZOS)
        
        # Add offsets to the image data directly if model is b1 (maybe necessary for other models too?)
        if model == "b1":
            if vertical_offset > 0 or horizontal_offset > 0:
                new_image = Image.new("RGB", (label_image.width + horizontal_offset, label_image.height + vertical_offset), (255, 255, 255))
                new_image.paste(label_image, (horizontal_offset, vertical_offset))
                label_image = new_image
        
        # Print labels
        asyncio.run(self._print(model, density, label_image, n_copies, vertical_offset, horizontal_offset))
        

    async def _print(self, model, density, image, quantity, vertical_offset, horizontal_offset):
        device = await find_device(model)
        printer = PrinterClient(device)
        if await printer.connect():
            if model == "b1":
                await printer.print_imageV2(image, density=density, quantity=quantity)
            else:
                await printer.print_image(image, density=density, quantity=quantity, vertical_offset=vertical_offset, horizontal_offset=horizontal_offset)

        await printer.disconnect()
