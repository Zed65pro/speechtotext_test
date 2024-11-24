import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from dotenv import load_dotenv
from utils.google_drive_api import GoogleDriveApi
from utils.transkriptor_api import TranskriptorApi
from utils.utils import get_audio_duration, save_result_to_local_file


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

    def upload_file(self):
        try:
            self.wav_file = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav"), ("MP3 Files", "*.mp3")])
            if self.wav_file:
                # Validate file duration (replace with actual duration check if required)
                duration_of_sound_file = get_audio_duration(self.wav_file)
                if duration_of_sound_file and duration_of_sound_file > 200:
                    messagebox.showerror("Error", "File must be less than 200 seconds.")
                    return

                self.upload_button.config(state="disabled")
                self.progress.pack()
                self.progress.start()
                threading.Thread(target=self.process_file).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload audio file: {e}")
            return None

    def process_file(self):
        try:
            # google_drive_url = GoogleDriveApi.upload_audio_file_to_google_drive(self.wav_file)
            # order_id = TranskriptorApi.transcribe_using_google_drive_url(google_drive_url)
            #
            # # Save results to JSON
            # self.save_results()
            #
            # # Success message
            # self.status_label.config(text=f"Processing complete! Results saved at {self.result_path}

            TranskriptorApi.get_order_status('123')
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
        save_result_to_local_file(self.result_path, result_data)


# Main App Execution
if __name__ == "__main__":
    load_dotenv()
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()
