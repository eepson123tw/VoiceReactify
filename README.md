# VoiceReactify

VoiceReactify is a React-based application that integrates audio processing with Text-to-Speech (TTS) functionalities. This project allows users to record audio, transcribe it into text using AI models, and optionally convert the text back into speech.
![record](https://github.com/user-attachments/assets/191c324c-0ec4-4e3b-9a96-e3e48dceb5df)

## Features

- **Audio Recording:** Capture audio directly from the browser.
- **Real-time Transcription:** Convert audio to text using advanced AI models.
- **Text-to-Speech:** Convert transcribed text back to speech using TTS.
- **React Integration:** Built using the React framework for a seamless user experience.

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Node.js
- npm or yarn
- Python (for backend processing)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/VoiceReactify.git
   cd VoiceReactify
   ```

2. **Install the frontend dependencies:**

   ```bash
   npm install
   ```

3. **Install the backend dependencies:**

   Navigate to the backend directory (if applicable) and install dependencies using pip:

   ```bash
   pip install -r requirements.txt

   pip download -r requirements_cuda.txt -d ./packages   #for the load local packages

   # need to change this because need to download

   @staticmethod
   def ask_tos(model_full_path):
      """Automatically agree to the terms of service"""
      tos_path = os.path.join(model_full_path, "tos_agreed.txt")
      print(" > Automatically agreeing to the terms of service:")
      print(' | > "I have purchased a commercial license from Coqui: licensing@coqui.ai"')
      print(' | > "Otherwise, I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml"')
      # 自动同意许可协议
      with open(tos_path, "w", encoding="utf-8") as f:
         f.write("I have read, understood and agreed to the Terms and Conditions.")
      return True

   ```

### Running the Application

1. **Start the frontend:**

   ```bash
   npm start
   ```

2. **Start the backend (if applicable):**

   ```bash
   python app.py
   ```

3. **Access the application:**

   Open your browser and go to `http://localhost:3000`.

## Usage

- **Record Audio:** Click on the record button to start capturing audio.
- **Transcribe Audio:** The recorded audio will automatically be transcribed into text.
- **Text-to-Speech:** Convert the transcribed text back into speech by clicking the "Speak" button.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
