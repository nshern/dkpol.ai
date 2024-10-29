from ODAFtpClient import ODAFtpClient
from transformer import Transformer


class ETLPipeline:
    def __init__(self, client: ODAFtpClient, transformer: Transformer):
        self.client = client
        self.transformer = transformer

    def run(self):
        self.client.download_files()
        self.transformer.run()
