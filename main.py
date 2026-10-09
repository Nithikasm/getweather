
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from weather import get_current_weather

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

import time

def main():
    user_input = input("What would you like to know? ")

    start = time.perf_counter()

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=user_input,
        config=types.GenerateContentConfig(tools=tools)
    )

    print(f"\nGemini first call: {time.perf_counter() - start:.2f}s")

    for part in response.candidates[0].content.parts:
        if part.function_call:
            function_call = part.function_call

            if function_call.name == "get_current_weather":
                weather_start = time.perf_counter()

                result = get_current_weather(
                    function_call.args["city_name"]
                )

                print(
                    f"WeatherAPI call: "
                    f"{time.perf_counter() - weather_start:.2f}s"
                )

                final_start = time.perf_counter()

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
                    config=types.GenerateContentConfig(tools=tools)
                )

                print(
                    f"Gemini final call: "
                    f"{time.perf_counter() - final_start:.2f}s"
                )
                print(f"\n{final_response.text}")
                return

    print(response.text)


if __name__ == "__main__":
    main()