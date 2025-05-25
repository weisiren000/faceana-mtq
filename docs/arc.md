# Project Architecture

```
.
├── .env
├── .env.example
├── .gitignore
├── README-CN.md
├── README.md
├── requirements.txt
├── docs/
│   ├── agent.md
│   ├── arc.md
│   ├── idea.md
│   └── init/
├── src/
│   ├── config.py
│   ├── main.py
│   ├── _backend/
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── agent/
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── anthropic.py
│   │   │   ├── facepp.py
│   │   │   ├── gemini.py
│   │   │   ├── openai.py
│   │   │   └── openrouter.py
│   │   ├── core/
│   │   │   └── __init__.py
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   ├── anthropic.py
│   │   │   ├── gemini.py
│   │   │   ├── openai.py
│   │   │   ├── openrouter.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── prompt.py
│   ├── _frontend/
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── components/
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   └── __init__.py
│   │   └── views/
│   │       └── __init__.py
│   ├── arduino_link/
│   │   └── __init__.py
│   ├── comfyui_link/
│   │   └── __init__.py
│   └── touchdesigner_link/
│       └── __init__.py
