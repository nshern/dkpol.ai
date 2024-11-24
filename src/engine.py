import os
from pathlib import Path

from llama_index.core import (
    Document,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.memory import ChatMemoryBuffer


class Engine:
    def __init__(
        self,
        system_prompt="Besvar spørgsmål med udgangspunkt i det materiale du har til rådighed,\
        Hvis ikke du kan besvare spørgsmålet med udgangspunkt i materialet, \
        som du har til rådighed, skal du siges at du ikke kan finde svaret i materialet. \
        Du skal kun rådgive med udgangspunkt i materialet. Giv ikke generel vejledning. \
        Svar kun på dansk\
        ",
        chunk_size=1024,
        similarity_top_k=5,
    ):
        self.system_prompt = system_prompt
        self.chunk_size = chunk_size
        self.similarity_top_k = similarity_top_k

        self.index_dir = f"{os.path.dirname(__file__)}/../data/storage/"
        self.documents_path = f"{os.path.dirname(__file__)}/../data/parsed/"

        print(f"{self.documents_path}")

        if not Path(self.index_dir).exists():
            # if not os.path.isfile(self.documents_path):
            #     raise ValueError("No files were found. Need to run ETL module.")

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

    def reset(self):
        self.chat_engine.reset()

    def __prepare_documents_for_indexing(self):
        documents = []

        for file in Path(self.documents_path).iterdir():
            with open(file, "r") as file:
                text = file.read()

            document = Document(text=text)

            documents.append(document)

        return documents

        #
        # if data is not None:
        #     for i in data:
        #         document = Document(
        #             text=self.__strip_blank_lines(i["content_transformed"]),
        #             metadata={
        #                 "url": i["url"],
        #             },
        #             excluded_llm_metadata_keys=["time"],
        #             metadata_seperator="::",
        #             metadata_template="{key}=>{value}",
        #             text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        #         )
        #
        #         documents.append(document)
        # else:
        #     raise ValueError("data is None")
        #
        # return documents

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
            # if include_sources:
            #     print(f"{BOLD}Kildehenvisning:{RESET}")
            #     for i in get_urls_from_sources(response):
            #         print(f"{ITALIC}- {i}{RESET}")

    def chat(self, query):
        return self.chat_engine.chat(query)


if __name__ == "__main__":
    e = Engine()
    e.repl_chat(include_sources=False)
