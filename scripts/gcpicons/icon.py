# Copyright (c) 2020 David Holsgrove
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/davidholsgrove/gcp-icons-for-plantuml/blob/master/LICENSE-CODE)
"""
Modules to support creation of PlantUML icon files
"""

import re
import subprocess
import sys
from subprocess import PIPE

from PIL import Image

PUML_LICENSE_HEADER = """' Copyright (c) 2020 David Holsgrove
' Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
' SPDX-License-Identifier: CC-BY-ND-2.0 (For details, see https://github.com/davidholsgrove/gcp-icons-for-plantuml/blob/master/LICENSE-CODE)
"""


class Icon:
    """Reference to source PNG and methods to create the PUML icons"""

    def __init__(self, posix_filename, config):
        self.filename = posix_filename
        self.config = config

        # If config provided, set other values
        # If no config provided, used to access internal methods only
        if self.config:
            # Source name and category to uniquely identify same file names
            # in different categories to apply color or other values
            self.source_name = str(posix_filename).split("/")[-1]
            self.source_category = str(posix_filename).split("/")[3]
            self._set_values(self.source_name, self.source_category)

    def generate_image(
        self, path, color=True, max_target_size=128, transparency=False
    ):
        """Create image from filename and save full color without transparency to path"""
        im = Image.open(self.filename)
        im.thumbnail((max_target_size, max_target_size))
        if not transparency:
            im = self._remove_transparency(im)
        # Save color image
        im.save(f"{path}/{self.target}.png", "PNG")
        return

    def generate_puml(self, path):
        """Generate puml file for service"""
        puml_content = PUML_LICENSE_HEADER
        # Start plantuml.jar and encode sprite from main PNG
        try:
            target = self.target
            color = self.color
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    "./plantuml.jar",
                    "-encodesprite",
                    "16z",
                    f"{path}/{target}.png",
                ],
                shell=False,
                stdout=PIPE,
                stderr=PIPE,
            )
            puml_content += result.stdout.decode("UTF-8")
            puml_content += f"GCPEntityColoring({target})\n"
            puml_content += f"!define {target}(e_alias, e_label, e_techn) GCPEntity(e_alias, e_label, e_techn, {color}, {target}, {target})\n"
            puml_content += f"!define {target}(e_alias, e_label, e_techn, e_descr) GCPEntity(e_alias, e_label, e_techn, e_descr, {color}, {target}, {target})\n"
            puml_content += f"!define {target}Participant(p_alias, p_label, p_techn) GCPParticipant(p_alias, p_label, p_techn, {color}, {target}, {target})\n"
            puml_content += f"!define {target}Participant(p_alias, p_label, p_techn, p_descr) GCPParticipant(p_alias, p_label, p_techn, p_descr, {color}, {target}, {target})\n"

            with open(f"{path}/{target}.puml", "w") as f:
                f.write(puml_content)

        except Exception as e:
            print(f"Error executing plantuml jar file, {e}")
            sys.exit(1)

    # Internal methods
    def _set_values(self, source_name, source_category):
        """Set values if entry found, otherwise set uncategorized and defaults"""
        for i in self.config["Categories"]:
            for j in i["Services"]:
                if (
                    j["Source"] == source_name
                    and i["SourceDir"] == source_category
                ):
                    try:
                        self.category = i["Name"]
                        self.target = j["Target"]

                        # Set color from service, category, default then black
                        if "Color" in j:
                            self.color = self._color_name(j["Color"])
                        elif "Color" in i:
                            self.color = self._color_name(i["Color"])
                        elif "Color" in self.config["Defaults"]["Category"]:
                            self.color = self._color_name(
                                self.config["Defaults"]["Category"]["Color"]
                            )
                        else:
                            print(
                                f"No color definition found for {source_name}, using black"
                            )
                            self.color = "#000000"
                        return
                    except KeyError as e:
                        print(f"Error: {e}")
                        print(
                            "config.yml requires minimal config section, please see documentation"
                        )
                        sys.exit(1)
                    except TypeError as e:
                        print(f"Error: {e}")
                        print(
                            "config.yml requires Defaults->Color definition, please see documentation"
                        )
                        sys.exit(1)

        # Entry not found, place into uncategorized
        try:
            self.category = "Uncategorized"
            self.target = self._make_name(self.source_name)
            self.color = self.config["Defaults"]["Category"]["Color"]
        except KeyError as e:
            print(f"Error: {e}")
            print(
                "config.yml requires minimal config section, please see documentation"
            )
            sys.exit(1)

    # def _set_values(self, source_name, source_category):
    #     """Set values if entry found, otherwise set uncategorized and defaults"""
    #     for i in self.config["Categories"]:
    #         for j in i["Services"]:
    #             if j["Source"] == source_name:
    #                 try:
    #                     self.category = i["Name"]
    #                     self.target = j["Target"]

    #                     # Set color from service, category, default then black
    #                     if "Color" in j:
    #                         self.color = self._color_name(j["Color"])
    #                     elif "Color" in i:
    #                         self.color = self._color_name(i["Color"])
    #                     elif "Color" in self.config["Defaults"]["Category"]:
    #                         self.color = self._color_name(
    #                             self.config["Defaults"]["Category"]["Color"]
    #                         )
    #                     else:
    #                         print(
    #                             f"No color definition found for {source_name}, using black"
    #                         )
    #                         self.color = "#000000"
    #                     return
    #                 except KeyError as e:
    #                     print(f"Error: {e}")
    #                     print(
    #                         "config.yml requires minimal config section, please see documentation"
    #                     )
    #                     sys.exit(1)
    #                 except TypeError as e:
    #                     print(f"Error: {e}")
    #                     print(
    #                         "config.yml requires Defaults->Color definition, please see documentation"
    #                     )
    #                     sys.exit(1)

    #     # Entry not found, place into uncategorized
    #     try:
    #         self.category = "Uncategorized"
    #         self.target = self._make_name(self.source_name)
    #         self.color = self.config["Defaults"]["Category"]["Color"]
    #     except KeyError as e:
    #         print(f"Error: {e}")
    #         print(
    #             "config.yml requires minimal config section, please see documentation"
    #         )
    #         sys.exit(1)

    def _make_name(self, name=None):
        """Create PUML friendly name short name without directory or .png,
        then remove leading GCP to reduce length. Also convert non-alphanumeric characters to underscores"""

        if name:
            new_name = name.split("/")[-1]
            if new_name.startswith(("GCP-")):
                new_name = new_name.split("-", 1)[1]
            # Replace non-alphanumeric with underscores (1:1 mapping)
            new_name = re.sub(r"\W+", "_", new_name)
        return new_name

    def _color_name(self, color_name):
        """Returns hex color for provided name from config Defaults"""
        try:
            for color in self.config["Defaults"]["Colors"]:
                if color == color_name:
                    return self.config["Defaults"]["Colors"][color]
            print(
                f"ERROR: Color {color_name} not found in default color list, returning Black"
            )
            return "#4284F3"
        except KeyError as e:
            print(f"Error: {e}")
            print(
                "config.yml requires minimal config section, please see documentation"
            )
            sys.exit(1)

    def _remove_transparency(self, im, bg_colour=(255, 255, 255)):
        """remove transparency from image and background color, default white"""
        # Only process if image has transparency (http://stackoverflow.com/a/1963146)
        if im.mode in ("RGBA", "LA") or (
            im.mode == "P" and "transparency" in im.info
        ):
            # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
            alpha = im.convert("RGBA").split()[-1]
            bg = Image.new("RGBA", im.size, bg_colour + (255,))
            bg.paste(im, mask=alpha)
            return bg
        else:
            return im
