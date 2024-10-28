import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s %(message)s"
)


class Transformer:

    def __init__(self, input_dir: Path, output_dir: Path):
        # Directory where the transformer should take the raw files from
        self.input_dir = input_dir
        self.output_dir = output_dir

    # def _extract_date_from_xml(self, file):
    #     res = []
    #     with open(file, "r") as f:
    #         xml_data = f.read()
    #     root = ET.fromstring(xml_data)
    #
    #     dates = root.findall(".//DateOfSitting")
    #     res = dates[0].text
    #
    #     return res

    def __parse_raw_xml_file(self, file):
        res = []
        with open(file, "r") as f:
            xml_data = f.read()

        try:
            root = ET.fromstring(xml_data)
        except Exception as e:
            logging.debug(f"exception: {e}")
            return

        dagsordenspunkter = root.findall(".//DagsordenPunkt")
        id = 0
        for i in dagsordenspunkter:
            id += 1
            tale = i.findall(".//Tale")
            for k in tale:
                firstname = k.find(".//Taler/MetaSpeakerMP/OratorFirstName")
                if firstname is not None:
                    firstname = firstname.text
                lastname = k.find(".//Taler/MetaSpeakerMP/OratorLastName")
                if lastname is not None:
                    lastname = lastname.text
                text_snippet = k.findall(".//TaleSegment/TekstGruppe/Exitus/Linea/Char")
                text = " ".join([i.text for i in text_snippet if i.text is not None])
                line = f"**{firstname} {lastname}**: {text}\n"
                res.append(line)

        return " ".join(res)

    def __parse_raw_xml_files(self):
        folders = os.listdir(self.input_dir)

        for folder in folders:
            files = os.listdir(f"{self.input_dir}/{folder}")

            for file in files:
                filename = f"data/raw/{folder}/{file}"
                logging.debug(f"parsing {folder}/{file}")
                parsed = self.__parse_raw_xml_file(filename)

                parsed_file_title = f"{self.output_dir}/parsed_{file}"

                if parsed is not None:
                    with open(parsed_file_title, "w") as f:
                        f.write(parsed)
                else:
                    return

    def run(self):
        logging.info("parsing...")
        self.__parse_raw_xml_files()
