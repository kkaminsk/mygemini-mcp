# Example: How Google API Key is Used in MyGemini MCP Server
# This shows how the GEMINI_API_KEY from .env is used server-side

import google.generativeai as genai
from config.settings import get_settings

def example_gemini_usage():
    """Example showing how Google API key is used on the server side"""
    
    # 1. Load settings from .env file
    settings = get_settings()
    
    # 2. Configure Google Generative AI with the API key
    if settings.gemini_api_key:
        genai.configure(api_key=settings.gemini_api_key)
        
        # 3. Create a model instance
        model = genai.GenerativeModel('gemini-pro')
        
        # 4. Use the model (this would be called by MCP tools)
        response = model.generate_content("Hello, how are you?")
        
        return response.text
    else:
        raise ValueError("GEMINI_API_KEY not configured in .env file")

# Example MCP tool that uses Gemini
async def gemini_chat_tool(prompt: str) -> dict:
    """Example MCP tool that uses the Google API key to call Gemini"""
    
    settings = get_settings()
    
    if not settings.gemini_api_key:
        return {
            "content": "Error: GEMINI_API_KEY not configured",
            "structuredContent": {"error": "missing_api_key"}
        }
    
    try:
        # Configure Gemini with the server's API key
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate response using Google's API
        response = model.generate_content(prompt)
        
        return {
            "content": response.text,
            "structuredContent": {
                "model": "gemini-pro",
                "prompt": prompt,
                "response": response.text
            }
        }
        
    except Exception as e:
        return {
            "content": f"Error calling Gemini API: {str(e)}",
            "structuredContent": {"error": str(e)}
        }

if __name__ == "__main__":
    # Test the configuration
    settings = get_settings()
    print(f"Gemini API Key configured: {'Yes' if settings.gemini_api_key else 'No'}")
    print(f"API Key starts with: {settings.gemini_api_key[:10] + '...' if settings.gemini_api_key else 'Not set'}")
