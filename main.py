import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, UrlContext

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini client with API key from environment
API_KEY = os.getenv("GOOGLE_API_KEY")

class GeminiChatAgent:
    def __init__(self):
        if not API_KEY:
            logger.error("GOOGLE_API_KEY not found in environment variables.")
            raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
        
        # Initialize client
        self.client = genai.Client(api_key=API_KEY)
        self.model_id = "gemini-2.5-flash-preview-05-20"
        
        # Only keeping wiki URL as reference
        self.wiki = "https://pd2reawakening.com/wiki/index.php?title=Main_Page"
        
        # Initialize tools
        self.url_context_tool = Tool(
            url_context=UrlContext
        )
        
        self.google_search_tool = Tool(
            google_search=GoogleSearch
        )
        
        # Initialize conversation history - using user and model roles only as system is not supported
        self.conversation_history = []
        
        # Add instructions as a user message instead of system role
        initial_instructions = f"""
        [INSTRUCTIONS FOR ASSISTANT]
        # You are a helpful assistant specializing in Project Diablo 2.
        # You can access PD2 wiki information at {self.wiki}.
        # When a user asks a question about Project Diablo 2 game mechanics, items, skills, crafting recipes, or character builds, you must first attempt to find the answer by browsing the official Project Diablo 2 wiki (https://wiki.projectdiablo2.com/wiki/Main_Page). Only use the general search tool if browsing the wiki directly doesn't yield relevant results or if the query is broader than specific game data.
        ## If you have a result but not from project diablo 2 wikis, nor the internet, try check https://wiki.projectdiablo2.com/wiki/Patch_Notes to confirm (example: spirit rw sword have +1 all skills instead 2)
        ## The user may provide character URLs or guide URLs in the conversation.
        ## Use this information to help the user with their Diablo 2 character.
        ## When asked about skill damage for a skill, if the synergy details (level, all synergies or somes) are not specified in the user's query, I must ask the user to "Please provide the level of relevant synergies if you'd like a calculation based on them." before attempting to calculate the total damage.
        1.  **Prioritize the Project Diablo 2 Wiki:** My first point of reference will always be the official PD2 wiki ([https://wiki.projectdiablo2.com/wiki/Main_Page](https://wiki.projectdiablo2.com/wiki/Main_Page)). I'll attempt to find the specific item directly there.
        2.  **Use the `browse` tool comprehensively:** Once I identify a relevant wiki URL (or any other reliable PD2 source), I will use the `browse` tool to read its content.
        3.  **Actively identify variable stats:** While browsing, I will specifically look for:
            *   Numbers presented as a range (e.g., `[X-Y]`, `X-Y`).
            *   Keywords like "variable," "random," "min/max," "up to," "can roll."
            *   Any stat that isn't a fixed, single value.
        4.  **Report all relevant modifiers and their ranges:** My response will include:
            *   The item's name and type.
            *   All significant modifiers, clearly indicating which ones are variable and their full possible range.
            *   Any crucial base stats (e.g., defense, block, socket potential).
            *   Any other unique properties that define the item.
        5.  **Cite the source:** I will always provide the direct URL to the wiki page or other source from which the information was obtained.
        6.  **Confirm (if necessary):** If the information found is ambiguous, seems outdated, or if a user provides a specific detail that contradicts what I found, I will use `concise_search` with targeted queries (e.g., "PD2 [item name] patch notes") or check the Project Diablo 2 patch notes wiki ([https://wiki.projectdiablo2.com/wiki/Patch_Notes](https://wiki.projectdiablo2.com/wiki/Patch_Notes)) to confirm the most current statistics.
        Please respond to the following message from the user.
        [END INSTRUCTIONS]
        """
        
        # Add initial instructions as a user message
        self.add_user_message(initial_instructions)
        
        # Add a placeholder response from the model to acknowledge the instructions
        self.add_model_message("I understand. I'm a Project Diablo 2 assistant and will help with any questions about the game, characters, builds, or items. What would you like to know?")
    
    def add_user_message(self, message):
        """Add a user message to the conversation history."""
        user_message = {
            "role": "user",
            "parts": [{"text": message}]
        }
        self.conversation_history.append(user_message)
        return user_message
    
    def add_model_message(self, message):
        """Add a model message to the conversation history."""
        model_message = {
            "role": "model",
            "parts": [{"text": message}]
        }
        self.conversation_history.append(model_message)
        return model_message
    
    def generate_response(self, user_message):
        """Generate a response to the user's message."""
        # Add user message to history
        self.add_user_message(user_message)
        
        try:
            logger.info("Sending request to Gemini API...")
            
            # Generate content with tools and history
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=self.conversation_history,
                config=GenerateContentConfig(
                    tools=[self.url_context_tool, self.google_search_tool],
                    response_modalities=["TEXT"],
                )
            )
            
            logger.info("Response received from Gemini API")
            
            # Process the response
            if not response or not hasattr(response, 'candidates') or not response.candidates:
                error_msg = "No valid response received from Gemini API"
                logger.error(error_msg)
                return error_msg
                
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                error_msg = "No content in response candidate"
                logger.error(error_msg)
                return error_msg
                
            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                error_msg = "No parts in content"
                logger.error(error_msg)
                return error_msg
            
            # Extract the response text
            response_text = ""
            for part in candidate.content.parts:
                if hasattr(part, 'text'):
                    response_text += part.text
            
            # Add response to conversation history
            self.add_model_message(response_text)
            
            # Log URL context metadata if available
            if hasattr(candidate, 'url_context_metadata') and candidate.url_context_metadata:
                logger.info(f"URL context metadata: {candidate.url_context_metadata}")
                response_text += f"\n\n[URL Sources: {candidate.url_context_metadata}]"
            
            return response_text
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

def main():
    print("Welcome to the Project Diablo 2 Chat Assistant!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("-" * 50)
    print("Tip: You can provide character URLs or guide URLs in your messages.")
    print("-" * 50)
    
    try:
        # Initialize the chat agent
        agent = GeminiChatAgent()
        
        # Initial greeting
        print("Assistant: How can I help with your Project Diablo 2 character today?")
        
        # Main conversation loop
        while True:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Check for exit command
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nAssistant: Thanks for chatting! Good luck in your adventures!")
                break
            
            # Generate and display response
            print("\nAssistant: ", end="")
            response = agent.generate_response(user_input)
            print(response)
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set up your GOOGLE_API_KEY in the .env file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
