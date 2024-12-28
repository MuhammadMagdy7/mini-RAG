from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnums 
import cohere
import logging
import time

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str, 
                        default_input_max_characters: int=1000,
                        default_generation_max_output_tokens: int=1000,
                        default_generation_temperature: float=0.1 ):

        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.ClientV2(
            api_key = self.api_key,
        )

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str,chat_history :list = [], max_output_tokens: int=None, temperature: float=None):

        if not self.client :
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id :
            self.logger.error("generation model for CoHere was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=CoHereEnums.USER.value)
        )

        response = self.client.chat( 
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature    
        )

# response.message.content[0].text
        if not response or not response.message or len(response.message) == 0 or not response.message.content[0].text :
            self.logger.error("Error while generationg text with CoHere")
            return None
        
        return response.message.content[0].text

    def embed_text(self, text: str, document_type: str= None):
        
        if not self.client :
            self.logger.error("CoHere client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Eebedding model for CoHere was not set")
            return None
        

        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnums.QUERY:
            input_type = CoHereEnums.QUERY

        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type= input_type,
            embedding_types=['float']
        )
        # response.embeddings.float
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None

        return response.embeddings.float[0]

    # def embed_text(self, text: str, document_type: str = None, max_retries: int = 3):
    #   if not self.client:
    #       self.logger.error("CoHere client was not set")
    #       return None

    #   if not self.embedding_model_id:
    #       self.logger.error("Embedding model for CoHere was not set")
    #       return None

    #   input_type = CoHereEnums.DOCUMENT
    #   if document_type == DocumentTypeEnums.QUERY:
    #       input_type = CoHereEnums.QUERY

    #   retries = 0
    #   while retries < max_retries:
    #       try:
    #           response = self.client.embed(
    #               model=self.embedding_model_id,
    #               texts=[self.process_text(text)],
    #               input_type=input_type,
    #               embedding_types=['float']
    #           )
    #           if not response or not response.embeddings or not response.embeddings.float:
    #               self.logger.error("Error while embedding text with CoHere")
    #               return None

    #           return response.embeddings.float[0]

    #       except cohere.errors.TooManyRequestsError as e:
    #           self.logger.error(f"Rate limit exceeded: {e}. Retrying in 10 seconds...")
    #           time.sleep(10)  # زيادة فترة الانتظار إلى 10 ثوانٍ
    #           retries += 1

    #   self.logger.error("Max retries exceeded for embedding text with CoHere")
    #   return None

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role, 
            "content" : self.process_text(prompt)
        }
