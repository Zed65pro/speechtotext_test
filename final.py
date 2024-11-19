import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import json
import os
import base64
from dotenv import load_dotenv
import nlpcloud
from pydub import AudioSegment
from sinatools.morphology import morph_analyzer
from sinatools.utils.parser import arStrip


class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech-to-Text Converter")
        self.root.geometry("450x350")
        self.root.resizable(False, False)

        self.wav_file = None
        self.transcribed_text = None
        self.summary = None
        self.lemmas = None
        self.detected_words = None
        self.result_path = "results/result.json"

        self.setup_ui()

    def setup_ui(self):
        # Title
        tk.Label(self.root, text="Speech-to-Text Converter", font=("Arial", 16, "bold")).pack(pady=10)

        # File Upload Section
        self.upload_button = tk.Button(self.root, text="Upload Sound File", command=self.upload_file)
        self.upload_button.pack(pady=20)

        # Status Section
        self.status_label = tk.Label(self.root, text="", font=("Arial", 12), wraplength=400)
        self.status_label.pack(pady=20)

        # Loading Animation
        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=300)
        self.progress.pack(pady=20)
        self.progress.pack_forget()  # Hide initially

        # Retry Button (Hidden Initially)
        self.retry_button = tk.Button(self.root, text="Try Again", command=self.reset_app)
        self.retry_button.pack_forget()

    def reset_app(self):
        self.status_label.config(text="")
        self.progress.pack_forget()
        self.retry_button.pack_forget()
        self.upload_button.config(state="normal")

    def get_audio_duration(self, file_path):
        try:
            audio = AudioSegment.from_file(file_path)
            duration_seconds = audio.duration_seconds

            return duration_seconds
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get audio duration: {e}")
            return None

    def upload_file(self):
        self.wav_file = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav"), ("MP3 Files", "*.mp3")])
        if self.wav_file:
            # Validate file duration (replace with actual duration check if required)
            duration_of_sound_file = self.get_audio_duration(self.wav_file)
            if duration_of_sound_file and duration_of_sound_file > 200:
                messagebox.showerror("Error", "File must be less than 200 seconds.")
                return

            self.upload_button.config(state="disabled")
            self.progress.pack()
            self.progress.start()
            threading.Thread(target=self.process_file).start()

    def process_file(self):
        try:
            load_dotenv()
            token = os.getenv("NLPCLOUD_TOKEN")
            if not token:
                raise ValueError("NLPCLOUD_TOKEN is not set in the environment.")

            # Speech-to-text process
            client = nlpcloud.Client("whisper", token, True)
            with open(self.wav_file, 'rb') as binary_file:
                binary_file_data = binary_file.read()
                base64_encoded_data = base64.b64encode(binary_file_data)
                base64_output = base64_encoded_data.decode('utf-8')

                asr_result = client.asr(encoded_file=base64_output, input_language='ar')
                self.transcribed_text = asr_result["text"]

            llama_client = nlpcloud.Client("finetuned-llama-3-70b", token, gpu=True)

            # Grammar correction client
            grammar_correction_result = llama_client.gs_correction(text=self.transcribed_text)
            self.transcribed_text = grammar_correction_result['correction']

            # Summarization process
            summary_result = llama_client.summarization(text=self.transcribed_text)
            self.summary = summary_result["summary_text"]

            # Morphological analysis
            analyzed_text = morph_analyzer.analyze(text=self.transcribed_text, task='lemmatization')
            self.lemmas = [arStrip(text=text['lemma']) for text in analyzed_text]

            # Detect specific words
            self.detected_words = [lemma for lemma in self.lemmas if lemma in self.get_detection_dict()]

            # Save results to JSON
            self.save_results()

            # Success message
            self.status_label.config(text=f"Processing complete! Results saved at {self.result_path}")
        except Exception as e:
            self.status_label.config(text=f"An error occurred: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.retry_button.pack()

    def save_results(self):
        result_data = {
            "full_text": self.transcribed_text,
            "summary": self.summary,
            "lemmas": self.lemmas,
            "detected_words": self.detected_words,
        }
        os.makedirs(os.path.dirname(self.result_path), exist_ok=True)
        with open(self.result_path, "w", encoding="utf-8") as result_file:
            json.dump(result_data, result_file, ensure_ascii=False, indent=4)

    @staticmethod
    def get_detection_dict():
        return {}


# Main App Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()
