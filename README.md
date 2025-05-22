# Project Diablo 2 Chat Assistant

An interactive AI chat assistant powered by Google's Gemini 2.5 Flash API that helps with Project Diablo 2 game information, character builds, item recommendations, and more.

## Features

- **Interactive Chat Interface**: Engage in natural language conversations about PD2
- **Wiki Integration**: Automatically references the PD2 wiki for accurate information
- **URL Context Support**: Share character URLs or build guides for personalized recommendations
- **Web Search Integration**: Finds supplementary information when needed
- **Persistent Chat History**: Maintains context throughout your conversation

## Requirements

- Python 3.12+
- Google API Key with access to Gemini models

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/gemini-pd2.git
   cd gemini-pd2
   ```

2. Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

Run the chat assistant:

```bash
uv run main.py
```

### Example Conversations

```
You: What's the best safety armor base for my Act 2 mercenary?
Assistant: For an Act 2 mercenary, the best safety armor base depends on their strength. 
Assuming your mercenary has normal strength, a Dusk Shroud (Str Req: 77) offers excellent 
defense with low strength requirements. If your mercenary has higher strength, consider 
Archon Plate (Str Req: 103) which provides the highest defense of the elite armor bases.
```

## Project Structure

- `main.py` - Main application with the interactive chat loop
- `pyproject.toml` - Project dependencies and metadata
- `.env` - Environment variables (API keys)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Project Diablo 2](https://www.projectdiablo2.com/)
- [PD2 Wiki](https://pd2reawakening.com/wiki/)
- [Google Generative AI](https://ai.google.dev/)
