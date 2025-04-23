# 🚀 Feather Wand Agent

## 📝 Description
Feather Wand Agent is a comprehensive AI-powered toolkit for performance testing and monitoring. It integrates multiple industry-standard performance testing tools (JMeter, k6, Gatling, and Locust) into a single, unified interface, allowing users to execute and analyze performance tests through natural language interactions.

## ✨ Features
- 🏗️ Multi-tool agent framework supporting JMeter, k6, Gatling, and Locust
- 🤖 AI-powered conversational interface for executing performance tests
- 🧪 Unit testing utilities for ensuring agent reliability
- 📊 Performance metrics collection and analysis
- 🕵️‍♂️ Monitoring capabilities for test execution
- 🔄 Environment variable configuration for flexible deployment

## 🛠️ Prerequisites
- Python 3.8+
- JMeter (for JMeter tests)
- k6 (for k6 tests)
- Maven or Gradle (for Gatling tests)
- Locust (for Locust tests)

## 📋 Installation

0. Get a Google API key from either:

- https://console.developers.google.com/ (for Google Cloud)
- https://aistudio.google.com (for Google AI Studio)

Save this API key in the .env file, which will be created in step 3 of the installation process

```bash
# If using Gemini via Google AI Studio
GOOGLE_GENAI_USE_VERTEXAI="False"
GOOGLE_API_KEY="<YOUR_GOOGLE_API_KEY>"

# # If using Gemini via Vertex AI on Google Cloud
# GOOGLE_CLOUD_PROJECT="your-project-id"
# GOOGLE_CLOUD_LOCATION="your-location" #e.g. us-central1
# GOOGLE_GENAI_USE_VERTEXAI="True"
```

1. Clone the repository:
```bash
git clone https://github.com/yourusername/perf_tools_google_agent.git
cd perf_tools_google_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (copy .env.example to .env and modify as needed):
```bash
cp .env.example .env
```

## 🏃‍♂️ Usage

### Starting the Agent
Launch the agent web interface:
```bash
adk web
```

This will start the agent at http://localhost:8000, where you can interact with it through the chat interface.

### Supported Performance Testing Tools

#### JMeter
The agent can execute JMeter test plans (.jmx files) in both GUI and non-GUI modes with customizable duration and virtual user count.

**Example commands:**
- Run in non-GUI mode (default):
  ```
  Run my JMeter test at /path/to/test.jmx
  ```
- Run in non-GUI mode (with custom settings):
  ```
  Run my JMeter test at /path/to/test.jmx with 20 users and 300 seconds
  ```
- Run in GUI mode:
  ```
  Open JMeter GUI with my test plan at /path/to/test.jmx
  ```

#### k6
The agent can execute k6 scripts (.js files) with customizable duration and virtual user count.

**Example commands:**
- Run with default settings (30s duration, 10 VUs):
  ```
  Execute k6 script at /path/to/script.js
  ```
- Run with custom settings:
  ```
  Run k6 test at /path/to/script.js with 50 users for 2 minutes
  ```

#### Locust
The agent can execute Locust test files (.py files) with configurable parameters.

**Example commands:**
- Run with default settings:
  ```
  Run Locust test at /path/to/test.py
  ```
- Run with custom settings:
  ```
  Execute Locust test at /path/to/test.py against http://example.com with 200 users at spawn rate 20
  ```

#### Gatling
The agent can execute Gatling simulations using either Maven or Gradle as the runner.

**Example commands:**
- Run a Gatling simulation:
  ```
  Run Gatling test in directory /path/to/gatling/project
  ```
- Run a specific simulation class:
  ```
  Execute Gatling simulation MySimulation in directory /path/to/gatling/project
  ```

## 🔧 Configuration

The agent can be configured through environment variables in the .env file:

### General Configuration
- `FEATHERWAND_NAME`: Name of the agent (default: featherwand_agent)
- `FEATHERWAND_MODEL`: AI model to use (default: gemini-2.0-flash-exp)
- `FEATHERWAND_DESCRIPTION`: Description of the agent

### JMeter Configuration
- `JMETER_BIN`: Path to JMeter binary (default: jmeter)
- `JMETER_JAVA_OPTS`: Java options for JMeter

### k6 Configuration
- `K6_BIN`: Path to k6 binary (default: k6)

### Locust Configuration
- `LOCUST_BIN`: Path to Locust binary (default: locust)
- `LOCUST_HOST`: Default host to test (default: http://localhost:8089)
- `LOCUST_USERS`: Default number of users (default: 100)
- `LOCUST_SPAWN_RATE`: Default spawn rate (default: 10)
- `LOCUST_RUNTIME`: Default runtime (default: 30s)
- `LOCUST_HEADLESS`: Whether to run in headless mode (default: true)

### Gatling Configuration
- `GATLING_RUNNER`: Runner to use for Gatling (default: mvn, alternative: gradle)

## 📁 Project Structure
```
perf_tools_google_agent/
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── multi_tool_agent/     # Main agent code
│   ├── __init__.py       # Package initialization
│   ├── agent.py          # Agent definition and tools
│   ├── jmeter_utils.py   # JMeter utilities
│   ├── k6_utils.py       # k6 utilities
│   ├── locust_utils.py   # Locust utilities
│   ├── gatling_utils.py  # Gatling utilities
│   ├── prompt.py         # Agent prompts
│   ├── sample/           # Sample test files
│   └── tests/            # Unit tests
```

## 🧪 Testing
```bash
pytest tests/unit/
```

## 🤝 Contributing
Contributions are welcome! Please ensure tests pass before submitting pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License
MIT
