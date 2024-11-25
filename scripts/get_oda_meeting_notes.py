from pathlib import Path

from FtpDownloadClient import FtpDownloadClient

download_directory = Path(f"{Path(__file__).parent.parent}/data/test")
server_address = "oda.ft.dk"
source_path = "ODAXML/Referat/samling"

client = FtpDownloadClient(
    download_directory=download_directory,
    ftp_server_address=server_address,
    ftp_source_path=source_path,
)

client.run()
