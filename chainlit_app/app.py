import chainlit as cl
from openai_tools import tools
from calendly_apis import Calendly
from openai import AsyncOpenAI
import ast
import os, json
from chainlit.playground.providers.openai import stringify_function_call
from dotenv import load_dotenv

load_dotenv()

# Create an instance of the OpenAI client
client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Function mapping
function_mapper = {
    "list_events": Calendly.list_events,
    "cancel_event": Calendly.cancel_event,
}

@cl.step(type="tool")
async def call_tool(tool_call, message_history):
    function_name = tool_call.function.name
    arguments = ast.literal_eval(tool_call.function.arguments)
    
    current_step = cl.context.current_step
    current_step.name = function_name
    current_step.input = arguments

    function_response = function_mapper[function_name](arguments)
    current_step.output = function_response
    current_step.language = "json"
    
    message_history.append(
        {
            "role": "function",
            "name": function_name,
            "content": function_response,
            "tool_call_id": tool_call.id,
        }
    )
    return function_response


@cl.step(type="llm")
async def call_gpt(message_history):
    settings = {
        "model": "gpt-3.5-turbo",
        "tools": tools,
        "tool_choice": "auto",
    }
    cl.context.current_step.generation = cl.ChatGeneration(
        provider="openai-chat",
        messages=[
            cl.GenerationMessage(
                formatted=m["content"], name=m.get("name"), role=m["role"]
            )
            for m in message_history
        ],
        settings=settings,
    )

    # Call the OpenAI API
    response = await client.chat.completions.create(
        messages=message_history, **settings
    )

    message = response.choices[0].message

    for tool_call in message.tool_calls or []:
        if tool_call.type == "function":
            await call_tool(tool_call, message_history)

    # Get final response to get answer in natural language
    final_response = await client.chat.completions.create(
        model=settings["model"],
        messages=message_history,
    )
    final_response = final_response.choices[0].message.content

    if message.content:
        cl.context.current_step.generation.completion = message.content
        cl.context.current_step.output = message.content

    elif message.tool_calls:
        completion = stringify_function_call(message.tool_calls[0].function)

        cl.context.current_step.generation.completion = completion
        cl.context.current_step.language = "json"
        cl.context.current_step.output = completion

    return message, final_response

@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "message_history",
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Current year is 2024"},
        ],
    )

    res = await cl.AskActionMessage(
        content="Welcome to your personal Calendly Chatbot\nPlease select an option below",
        actions=[
            cl.Action(
                name="own-token",
                value="own-token",
                label="Enter your own calendly access token",
            ),
            cl.Action(
                name="test-token", value="test-token", label="Proceed with Test token"
            ),
        ],
    ).send()

    token = os.environ.get("CALENDLY_TEST_TOKEN")

    # Give option to user to either use custom token or test token
    if res and res.get("value") == "own-token":
        res_custom = await cl.AskUserMessage(
            content="Please enter your own Calendly token", timeout=180
        ).send()
        token = res_custom["output"]

    elif res and res.get("value") == "test-token":
        pass

    # Update the token and user id in the Calendly class
    Calendly.update_attributes(token)

    await cl.Message(
        content="Your token has been set successfully. You can now proceed with the chatbot.",
        author="Answer",
    ).send()

@cl.on_message
async def message(message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    message, final_response = await call_gpt(message_history)
    await cl.Message(content=final_response, author="Answer").send()
