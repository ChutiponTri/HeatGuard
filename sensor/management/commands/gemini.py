from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage

class Gemini():
    def __init__(self, api_key):
        # Set up the LLM model
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)

    # Function to Interact with Gemini
    def prompt(self, user_input, context_json):
        # Construct prompt with context
        prompt = f"""
            Now, answer the following question based on the JSON health monitoring data:
            {user_input}
            Do not give JSON data in the answer.

            Here is the info collected by HeatGuard, a wearable system for real-time heatstroke risk assessment.
            {context_json}
            JSON data contains the following fields:

                "user_id": the ID of the user
                "username": the username of the wearer
                "timestamp": the time when the data was recorded (in ISO 8601 format)
                "heart_rate": heart rate in beats per minute
                "skin_temperature": temperature of the skin in degrees Celsius
                "ambient_temperature": surrounding air temperature
                "humidity": relative humidity percentage
                "skin_resistance": electrical skin resistance in ohms
                "risk": the risk level of heatstroke (can be "no risk", "low", "moderate", or "high")

            Use this data to interpret the user's current health state and whether an alert should be triggered. Avoid returning any raw JSON.
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response