import os
import xml.etree.ElementTree as ET


class Transformer:

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

        # if xml_data == "":
        #     return

        root = ET.fromstring(xml_data)

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

    def _parse_raw_xml_files(self):
        folders = os.listdir("data")

        for folder in folders:
            files = os.listdir(f"data/{folder}")

            for file in files:
                filename = f"data/{folder}/{file}"
                print(filename)
                parsed = self.__parse_raw_xml_file(filename)
                parsed_file_title = f"parsed/parsed_{file}"

                with open(parsed_file_title, "w") as f:
                    f.write(parsed)

    def run(self):
        self._parse_raw_xml_files()


if __name__ == "__main__":
    t = Transformer()
    t.run()
