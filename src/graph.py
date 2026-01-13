from graph_init import initialize_graph
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


db = sqlite3.connect(":memory:", check_same_thread=False)
memory = SqliteSaver(db)
# Initialize the graph
graph = initialize_graph()

# Compile the graph
runnable = graph.compile(checkpointer=memory)
print(runnable.input_schema)


# You can add code here to execute the graph or further actions.
thread = {"configurable": {"thread_id": "a"}}


human_message = HumanMessage(content="I want to rent a car")
messages = [human_message]

# Le code d'invocation doit être dans les endpoints API, pas au niveau module
# result = runnable.invoke({"messages":messages}, thread)

print("resultat de graph ")
 #print(result)

#print(result["response"])