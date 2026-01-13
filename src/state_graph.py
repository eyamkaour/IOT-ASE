#from typing import TypedDict, Annotated, Sequence, List
from typing import Annotated, Sequence, List
from typing_extensions import TypedDict
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    handled: Annotated[List[bool], operator.add]
    make_sense: Annotated[List[bool], operator.add]
    node: Annotated[List[str], operator.add]
    query: str = ""
    response: Annotated[List[str], operator.add]
    context: str = ""
    call: str = ""
    location_finder_results: dict= {}
