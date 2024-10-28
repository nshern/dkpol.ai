import json
import os
from pathlib import Path

from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI

from engine_settings import init_azure_settings
from utils import get_urls_from_sources


# Test
# Test
class Engine:

    def __init__(
        self,
        system_prompt="Besvar spørgsmål med udgangspunkt i det materiale du har til rådighed,\
        som er hele Nævnenes' hus hjemmeside. \
        Hvis ikke du kan besvare spørgsmålet med udgangspunkt i materialet, \
        som du har til rådighed, skal du siges at du ikke kan finde svaret i materialet. \
        Du skal kun rådgive med udgangspunkt i materialet. Giv ikke generel vejledning. \
        Svar kun på dansk\
        Nedenstående ikke-udtømmende liste er en række forkortelser, som muligvis kan blive anvendt til at referere til div. instanser:\
        - **pvanke**: Ankenævnet for Patenter og Varemærker\
        - **søfart**: Ankenævnet for Søfartsforhold\
        - **byf/bfn**: Byfornyelsesnævnene\
        - **byg**: Byggeklageenheden\
        - **dkbb**: Disciplinær- og klagenævnet for beskikkede bygningssagkyndige\
        - **dnfe**: Disciplinærnævnet for Ejendomsmæglere\
        - **ekn**: Energiklagenævnet\
        - **ean**: Erhvervsankenævnet\
        - **hb/helbred**: Helbredsnævnet\
        - **klfu**: Klagenævnet for Udbud\
        - **konank**: Konkurrenceankenævnet\
        - **mfkn**: Miljø- og Fødevareklagenævnet\
        - **mff/fkn**: Mæglingsteamet for Forbrugerklager og Forbrugerklagenævnet\
        - **plan/pkn:** Planklagenævnet\
        - **revisor**: Revisornævnet\
        - **tkn**: Teleklagenævnet\
        - **tvist**: Tvistighedsnævnet\
        - **KPO**: Klageportalen\
        ",
        chunk_size=1024,
        similarity_top_k=5,
    ):

        self.system_prompt = system_prompt
        self.chunk_size = chunk_size
        self.similarity_top_k = similarity_top_k

        self.index_dir = f"{os.path.dirname(__file__)}/../data/storage/"
        self.documents_path = f"{os.path.dirname(__file__)}/../data/documents.json"

        print(f"{self.documents_path}")

        if not Path(self.index_dir).exists():

            if not os.path.isfile(self.documents_path):
                raise ValueError("No files were found. Need to run ETL module.")

            documents = self.__prepare_documents_for_indexing()

            print("Creating index..")
            self.index = VectorStoreIndex.from_documents(documents)

            print("Persisting index..")
            self.index.storage_context.persist(persist_dir=self.index_dir)

            print("Index persisted.")

        else:
            print("Loading existant index..")
            storage_context = StorageContext.from_defaults(persist_dir=self.index_dir)
            self.index = load_index_from_storage(storage_context)
            print("Index was loaded.")

        memory = ChatMemoryBuffer.from_defaults(token_limit=100000)

        self.chat_engine = self.index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=self.system_prompt,
            similarity_top_k=self.similarity_top_k,
        )

    def init_azure_settings(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")

        api_version = "2023-07-01-preview"

        llm = AzureOpenAI(
            model="gpt-4o",
            deployment_name="nh-gpt4o",
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )

        # You need to deploy your own embedding model as well as your own chat completion model
        embed_model = AzureOpenAIEmbedding(
            model="text-embedding-ada-002",
            deployment_name="my-custom-embedding",
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )

        Settings.llm = llm
        Settings.embed_model = embed_model

    def __strip_blank_lines(self, text):
        res = []
        for i in text.split("\n"):
            if i.strip() != "":
                res.append(i)

        return "\n".join(res)

    def reset(self):
        self.chat_engine.reset()
        # print("initialized engine reset")

    def __prepare_documents_for_indexing(self):

        documents = []

        data = None
        with open(self.documents_path, "r") as file:
            data = json.load(file)

        if data is not None:
            for i in data:
                document = Document(
                    text=self.__strip_blank_lines(i["content_transformed"]),
                    metadata={
                        "url": i["url"],
                    },
                    excluded_llm_metadata_keys=["time"],
                    metadata_seperator="::",
                    metadata_template="{key}=>{value}",
                    text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
                )

                documents.append(document)
        else:
            raise ValueError("data is None")

        return documents

    def repl_chat(self, include_sources=True):
        """
        REPL-like chat that prints responses to STDOUT
        """

        BOLD = "\033[1m"
        ITALIC = "\033[3m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        RESET = "\033[0m"

        while True:
            query = input(f"{BOLD}{MAGENTA}User: {RESET}")
            response = self.chat_engine.chat(query)
            print(f"{BOLD}{CYAN}Chatbot:{RESET} { response }\n")

            # If include_sources parameter is se to true urls will be printed to STDOUT for each repsponse
            if include_sources == True:
                print(f"{BOLD}Kildehenvisning:{RESET}")
                for i in get_urls_from_sources(response):
                    print(f"{ITALIC}- {i}{RESET}")

    def chat(self, query):
        return self.chat_engine.chat(query)


if __name__ == "__main__":
    init_azure_settings()
    e = Engine()
