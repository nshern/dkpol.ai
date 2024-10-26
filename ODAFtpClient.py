import ftplib
import logging
from pathlib import Path


class ODAFtpClient:

    def __init__(self, root):
        self.__root = root
        logging.basicConfig(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def __connect(self):
        """
        This method connects to the oda.ft.dk database via ftp and returns a connection object
        """

        ftp = ftplib.FTP("oda.ft.dk")

        ftp.login()

        # Go to the directory where meeting notes are stored
        ftp.cwd("ODAXML/Referat/samling")

        return ftp

    def __create_folder(self, folder):
        """
        This method creates the output directory where the files are downloaded to
        """

        # Check if the root path exists and create it if not
        root = Path(self.__root)
        if not root.exists():
            root.mkdir()

        # Check if the folder exists and create it if not
        subfolder = root / folder
        if not subfolder.exists():
            logging.info("Creating %s", subfolder)
            subfolder.mkdir()

    def download_files(self):
        """
        Jeg har en flyvemaskine. Og den har vinger på
        """

        # Download counter is used for logging how many new files were downloaded
        downloaded_counter = 0

        # Establish connection and return ftp object
        ftp = self.__connect()

        # Get folders
        folders = ftp.nlst()

        for folder in folders:

            self.__create_folder(folder)

            ftp.cwd(folder)

            files = ftp.nlst()

            for file in files:

                file_name = f"{self.__root}/{folder}/{file}"

                if Path(file_name).exists():
                    logging.info("%s already downloaded.", file)

                else:
                    with open(file_name, "wb") as f:

                        ftp.retrbinary(f"RETR {file}", f.write)

                    logging.info("Downloaded %s to %s", file, f"{self.__root}/{folder}")
                    downloaded_counter += 1

            ftp.cwd("..")

        logging.info("%s new files were downloaded.", downloaded_counter)
        ftp.quit()
