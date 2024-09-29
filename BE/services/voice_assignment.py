import azure.cognitiveservices.speech as speechsdk
import json
import time
import difflib
import string
import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('../env/.env.local').resolve()
print(f"載入 .env 文件: {env_path}")  # 調試輸出
load_dotenv(dotenv_path=env_path)

if not env_path.is_file():
    print(f".env 文件不存在於: {env_path}")
    sys.exit(1)

subscription_key = os.getenv('AZURE_SPEECH_KEY')
region = os.getenv('AZURE_SPEECH_REGION')

if not subscription_key or not region:
    print("請設置環境變量 AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION")
    sys.exit(1)

def perform_pronunciation_assessment(audio_filename: str, reference_text: str):
    """執行發音評估並返回評估結果。"""
    if not os.path.isfile(audio_filename):
        print(f"音頻文件未找到: {audio_filename}")
        sys.exit(1)

    print("開始識別...")
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_filename)
    enable_miscue = True
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=enable_miscue
    )
    pronunciation_config.enable_prosody_assessment()

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    pronunciation_config.apply_to(speech_recognizer)

    done = False
    recognized_words = []
    fluency_scores = []
    prosody_scores = []
    durations = []

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """回調函數，接收到停止事件時設置done為True"""
        nonlocal done
        done = True

    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        """回調函數，處理每個識別結果"""
        pronunciation_result = speechsdk.PronunciationAssessmentResult(evt.result)
        nonlocal recognized_words, fluency_scores, prosody_scores, durations
        recognized_words += pronunciation_result.words
        fluency_scores.append(pronunciation_result.fluency_score)
        prosody_scores.append(pronunciation_result.prosody_score)
        json_result = evt.result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
        jo = json.loads(json_result)
        nb = jo['NBest'][0]
        durations.append(sum([int(w['Duration']) for w in nb['Words']]))

    # 連接回調函數
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # 開始連續識別
    speech_recognizer.start_continuous_recognition()
    print("開始發音評估...")

    while not done:
        time.sleep(0.5)

    speech_recognizer.stop_continuous_recognition()
    print("發音評估完成。")

    # 處理評估結果
    reference_words = [w.strip(string.punctuation).lower() for w in reference_text.split()]
    if enable_miscue:
        diff = difflib.SequenceMatcher(None, reference_words, [x.word.lower() for x in recognized_words])
        final_words = []
        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            if tag in ['insert', 'replace']:
                for word in recognized_words[j1:j2]:
                    if word.error_type == 'None':
                        word._error_type = 'Insertion'
                    final_words.append(word)
            if tag in ['delete', 'replace']:
                for word_text in reference_words[i1:i2]:
                    word = speechsdk.PronunciationAssessmentWordResult({
                        'Word': word_text,
                        'PronunciationAssessment': {
                            'ErrorType': 'Omission',
                        }
                    })
                    final_words.append(word)
            if tag == 'equal':
                final_words += recognized_words[j1:j2]
    else:
        final_words = recognized_words

    # 計算總體分數
    final_accuracy_scores = [w.accuracy_score for w in final_words if w.error_type != 'Insertion']
    accuracy_score = sum(final_accuracy_scores) / len(final_accuracy_scores) if final_accuracy_scores else 0
    fluency_score = sum([x * y for x, y in zip(fluency_scores, durations)]) / sum(durations) if durations else 0
    completeness_score = len([w for w in recognized_words if w.error_type == "None"]) / len(reference_words) * 100
    completeness_score = min(completeness_score, 100)
    prosody_score = sum(prosody_scores) / len(prosody_scores) if prosody_scores else 0
    pron_score = accuracy_score * 0.4 + prosody_score * 0.2 + fluency_score * 0.2 + completeness_score * 0.2

    # 構建結果
    words_result = [
        {
            "word": word.word,
            "accuracy_score": word.accuracy_score,
            "error_type": word.error_type
        }
        for word in final_words
    ]

    result = {
        "pronunciation_score": pron_score,
        "accuracy_score": accuracy_score,
        "completeness_score": completeness_score,
        "fluency_score": fluency_score,
        "prosody_score": prosody_score,
        "words": words_result
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Azure 語音服務發音評估測試工具")
    parser.add_argument(
        '--audio',
        type=str,
        required=True,
        help='音頻文件的路徑（WAV格式）'
    )
    parser.add_argument(
        '--text',
        type=str,
        required=True,
        help='參考文本'
    )
    args = parser.parse_args()

    # 使用絕對路徑
    audio_file = os.path.abspath(args.audio)
    reference_text = args.text

    print(f"音頻文件: {audio_file}")
    print(f"參考文本: {reference_text}")

    result = perform_pronunciation_assessment(audio_file, reference_text)
    
    print("\n評估結果:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
