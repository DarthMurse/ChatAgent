# Introduction
This repository builds various chat agents with a web GUI interface. Here are the main features of the repo:
- Accept api keys of different LLM providers (openai, claude, deepseek, etc.), the user can manage the api keys in the web interface.
- Use `smolagents` as the library for building the agent.
- The web interface should support basic multi-turn chat function, open new chat function, choosing between models which the user has provided the api key.
- Put all the agent definition in the `agent` folder, and all the wrapper for different providers in the `provider` folder.
- Please support the rendering of markdown and latex formula in LLM outputs.
- Please save the api keys provided by the user so they don't need to provide it every time they restart the application.
- Support deleting preivous chat histories.