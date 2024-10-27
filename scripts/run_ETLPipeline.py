from pathlib import Path

from ETLPipeline import ETLPipeline
from ODAFtpClient import ODAFtpClient
from Transformer import Transformer

# Create download folder if it doesn't exist
download_folder = Path(f"{Path(__file__).parent.parent}/data/")

if not download_folder.exists():
    download_folder.mkdir()

pipeline = ETLPipeline(client=ODAFtpClient(download_folder), transformer=Transformer())
pipeline.run()
