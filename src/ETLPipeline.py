from FtpDownloadClient import FtpDownloadClient
from Transformer import Transformer


class ETLPipeline:
    def __init__(self, client: FtpDownloadClient, transformer: Transformer):
        self.client = client
        self.transformer = transformer

    # def run(self):
    #     self.client.download_files()
    #     self.transformer.run()
