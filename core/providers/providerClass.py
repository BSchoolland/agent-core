# core/providers/providerClass.py

# base class.  All providers will inherit from this class

from abc import ABC, abstractmethod

class Provider(ABC):
    def __init__(self, API_KEY = None):
        self.API_KEY = API_KEY
        self.ready = False

    # Perform any necessary initialization that the provider may need (for example, local LLM usage requires model loading)
    def initialize(self): 
        pass

    # generate a response from the provider
    @abstractmethod
    def generate_response(self, history, model):
        pass # will return tool calls and a message

    # convert standard history format to provider history format
    @abstractmethod
    def history_to_provider_format(self, history):
        pass 

    # convert provider history format back to standard history format
    @abstractmethod
    def provider_to_std_history_format(self, history):
        pass

    # convert tool information to a format that the provider can understand
    @abstractmethod
    def tool_to_provider_format(self, tool):
        pass

    

