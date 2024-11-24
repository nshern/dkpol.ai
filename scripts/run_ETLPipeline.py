from pathlib import Path

from ETLPipeline import ETLPipeline
from FtpDownloadClient import FtpDownloadClient
from Transformer import Transformer

# Create download folder if it doesn't exist
raw_folder = Path(f"{Path(__file__).parent.parent}/data/raw")
parsed_folder = Path(f"{Path(__file__).parent.parent}/data/parsed")


if not raw_folder.exists():
    raw_folder.mkdir()

if not parsed_folder.exists():
    parsed_folder.mkdir()


pipeline = ETLPipeline(
    client=FtpDownloadClient(
        raw_folder,
        ftp_server_address="oda.ft.dk",
        ftp_source_path="ODAXML/Referat/samling",
    ),
    transformer=Transformer(input_dir=raw_folder, output_dir=parsed_folder),
)
pipeline.run()
