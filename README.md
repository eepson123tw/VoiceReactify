# VoiceReactify

VoiceReactify is a React-based application that integrates audio processing with Text-to-Speech (TTS) functionalities. This project allows users to record audio, transcribe it into text using AI models, and optionally convert the text back into speech. It also supports voice assignment based on [Microsoft's Speech API](https://speech.microsoft.com/portal).

![intro](https://github.com/user-attachments/assets/56794705-edda-49c0-a318-9c1a39e5db9c)

## Features

- **Audio Recording**: Capture audio directly from the browser.
- **Real-time Transcription**: Convert audio to text using advanced AI models.
- **Text-to-Speech**: Convert transcribed text back to speech using TTS.
- **React Integration**: Built using the React framework for a seamless user experience.
- **Voice Assignment**: Use Microsoft's API to customize voice characteristics.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Docker Setup (Optional)](#docker-setup-optional)
- [Usage](#usage)
- [Important Notice](#important-notice)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- **Node.js**: Install from [here](https://nodejs.org/en/download/).
- **npm or yarn**: Comes with Node.js; yarn can be installed from [here](https://classic.yarnpkg.com/en/docs/install).
- **Python**: Required for backend processing. Install from [here](https://www.python.org/downloads/).
- **Docker** (Optional): For containerization. Install from [here](https://docs.docker.com/get-docker/).

### Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/VoiceReactify.git
   cd VoiceReactify
   ```

2. **Install Frontend Dependencies**

   ```bash
   cd frontend
   npm install
   # or
   yarn install
   ```

3. **Install Backend Dependencies**

   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

### Configuration

1. **Backend Environment Variables**

   Create a `env` file in the `backend` directory:

   ```.env.local
   AZURE_SPEECH_KEY = 'xxx'  
   AZURE_SPEECH_REGION = 'xxx'   
   ```

### Docker Setup (Optional)

If you prefer using Docker:

1. **Modify Terms of Service Agreement**

   Due to licensing requirements, you need to modify a backend file to automatically agree to the terms of service when running in Docker. See the [Important Notice](#important-notice) section below.

2. **Build Docker Images**

   ```bash
   docker-compose build
   ```

3. **Run Docker Containers**

   ```bash
   docker-compose up
   ```

## Usage



1. **Start the Backend Server**

   ```bash
   Make backend # in root
   --- or
   cd backend
   python app.py
   ```

2. **Start the Frontend Server**

   Open a new terminal window:

   ```bash
   Make frontend  # in root
   --- or
   cd frontend
   pnpm run dev
   ```

3. **Access the Application**

   Navigate to `http://localhost:5173` in your web browser.

4. **Record and Transcribe Audio**

   - Click on the **Record** button to start recording.
   - Click **Stop** to finish recording.
   - The audio will be transcribed into text automatically.

5. **Convert Text to Speech**

   - Choose a voice using the **Voice Assignment** feature.
   - Click on **Play** to hear the synthesized speech.(It is a icon)

## Important Notice

**Also, your computer needs to have enough memory to run this app.**

When running the application in Docker, you need to modify the backend code to automatically agree to the terms of service for certain AI models. This is necessary for downloading and using specific models within a containerized environment.

**Modify the `ask_tos` Method**

In the backend code, locate the `ask_tos` method and replace it with the following:

```python
@staticmethod
def ask_tos(model_full_path):
    """Automatically agree to the terms of service"""
    tos_path = os.path.join(model_full_path, "tos_agreed.txt")
    print(" > Automatically agreeing to the terms of service:")
    print(' | > "I have purchased a commercial license from Coqui: licensing@coqui.ai"')
    print(' | > "Otherwise, I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml"')
    # Automatically agree to the license agreement
    with open(tos_path, "w", encoding="utf-8") as f:
        f.write("I have read, understood and agreed to the Terms and Conditions.")
    return True
```

**Why This Change is Necessary**

- **Automatic Agreement**: This modification automates the acceptance of the terms of service, which is essential when running the application in a non-interactive Docker environment.
- **Model Download**: Without this change, the required models may not download correctly, causing the application to malfunction.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m 'Add YourFeature'
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
