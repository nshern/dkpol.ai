from pathlib import Path

from ETLPipeline import ETLPipeline
from ODAFtpClient import ODAFtpClient
from transformer import Transformer

# Create download folder if it doesn't exist
raw_folder = Path(f"{Path(__file__).parent.parent}/data/raw")
parsed_folder = Path(f"{Path(__file__).parent.parent}/data/parsed")


if not raw_folder.exists():
    raw_folder.mkdir()

if not parsed_folder.exists():
    parsed_folder.mkdir()


pipeline = ETLPipeline(
    client=ODAFtpClient(raw_folder),
    transformer=Transformer(input_dir=raw_folder, output_dir=parsed_folder),
)
pipeline.run()
