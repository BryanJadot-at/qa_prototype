
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatResult
from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain.schema.messages import (
    BaseMessage,
)
from typing import Optional, List, Mapping, Any

class ChatOpenAIWrapper(ChatOpenAI):
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        print('<request>\n')
        print(str(messages) + '\n')
        print('</request>\n')

        chat_result = super()._generate(messages, stop, run_manager, stream, **kwargs)
        
        #f = open('calls.log', 'a')

        

        #print('<response>\n')
        #print(str(chat_result.json()) + '\n')
        #print('</response>\n')
        #f.close()

        return chat_result

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        #print('<request>\n')
        #print(str(messages) + '\n')
        #print('</request>\n')

        chat_result = super()._agenerate(messages, stop, run_manager, stream, **kwargs)
        
        #f = open('calls.log', 'a')

        

        #print('<response>\n')
        #print(str(chat_result.json()) + '\n')
        #print('</response>\n')