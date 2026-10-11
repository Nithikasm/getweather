
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from weather import get_current_weather
from google.genai import errors
from validation import validate_city_name

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"),http_options=types.HttpOptions(timeout=30000))

tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_current_weather",
                description="Get current weather for a city.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "city_name": types.Schema(
                            type=types.Type.STRING,
                            description="The city to get weather for"
                        )
                    },
                    required=["city_name"]
                )
            )
        ]
    )
]
def execute_weather_tool(function_call):
                """Validate and safely execute the requested weather tool."""

                if function_call.name != "get_current_weather":
                    raise ValueError(
                        f"Unknown tool: {function_call.name}"
                    )

                args = function_call.args or {}

                if not isinstance(args, dict):
                    raise ValueError("Tool arguments must be an object.")

                city_name = validate_city_name(args.get("city_name"))

                print(f"Validation passed for city: {city_name}")
                return get_current_weather(city_name)

def main():
    user_input = input("What would you like to know? ")

    system_message = (
        "You are a helpful assistant. You have access to a weather tool. "
        "If the user asks for something unrelated to the weather (like making objects), "
        "politely decline. If the user provides an ambiguous or non-existent city, "
        "ask them to clarify the city name before invoking the tool."
    )

    try:
        response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_input,
                config=types.GenerateContentConfig(
                        tools=tools,
                        system_instruction=system_message
                )
            )
    except errors.ServerError as err:
            if err.code == 503:
                print("Gemini is temporarily busy. Please try again in a moment.")
            else:
                print(f"Gemini server error: {err.code}")
            return

    for part in response.candidates[0].content.parts:
        if part.function_call:
            function_call = part.function_call

            try:
                result = execute_weather_tool(function_call)
            except ValueError as err:
                result = {"error": str(err)}
            except Exception:
                result = {"error": "Weather lookup failed."}

            try:
                final_response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part(text=user_input)]
                        ),
                        response.candidates[0].content,
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_function_response(
                                    name=function_call.name,
                                    response=result
                                )
                            ]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        tools=tools,
                        system_instruction=system_message
                        )
                )
            except errors.ServerError as final_err: 
                if final_err.code == 503:
                    print("Gemini is temporarily busy. Your weather data was retrieved, but the final answer could not be generated. Please try again.")
                else:
                    print(f"Gemini server error: {final_err.code}")
                return
            
            print(f"\n{final_response.text}")
            return

    print(response.text)


if __name__ == "__main__":
    main()
