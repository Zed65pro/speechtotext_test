import tkinter as tk
from tkinter import filedialog, messagebox
import speech_recognition as sr
import threading
from pydub import AudioSegment


class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech-to-Text Converter")
        self.root.geometry("400x300")

        # Set up the UI components
        self.label = tk.Label(self.root, text="Choose a .wav file to convert to text")
        self.label.pack(pady=20)

        self.upload_button = tk.Button(self.root, text="Upload WAV File", command=self.upload_file)
        self.upload_button.pack(pady=10)

        self.progress_label = tk.Label(self.root, text="")
        self.progress_label.pack(pady=10)

        self.convert_button = tk.Button(self.root, text="Convert", state="disabled", command=self.convert_to_text)
        self.convert_button.pack(pady=20)

        self.download_button = tk.Button(self.root, text="Download", state="disabled", command=self.download_file)
        self.download_button.pack(pady=10)

        self.wav_file = None
        self.transcribed_text = ""
        self.export_path = "transcribed_text.txt"

    def upload_file(self):
        self.wav_file = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if self.wav_file:
            self.convert_button.config(state="normal")
            self.progress_label.config(text="File uploaded successfully!")

    def convert_to_text(self):
        if not self.wav_file:
            messagebox.showerror("Error", "Please upload a valid .wav file")
            return

        # Disable the convert button to prevent multiple conversions
        self.convert_button.config(state="disabled")

        # Start the process in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.process_file).start()

    def process_file(self):
        recognizer = sr.Recognizer()

        # Load the audio file using pydub
        audio = AudioSegment.from_wav(self.wav_file)
        total_duration = len(audio)  # in milliseconds
        chunk_duration = 60 * 1000  # 5 seconds in milliseconds

        # Process the audio in 5-second chunks
        for start_ms in range(0, total_duration, chunk_duration):
            end_ms = min(start_ms + chunk_duration, total_duration)
            chunk = audio[start_ms:end_ms]

            # Export the chunk to a temporary file for recognition
            chunk_path = "../temp_chunk.wav"
            chunk.export(chunk_path, format="wav")

            # Update UI progress
            self.progress_label.config(text=f"Transcribing chunk {start_ms // chunk_duration + 1}...")

            with sr.AudioFile(chunk_path) as audio_file:
                audio_data = recognizer.record(audio_file)
                try:
                    # Recognize speech for this chunk
                    chunk_text = recognizer.recognize_google(audio_data, language='ar-AR',
                                                             with_confidence=True)
                    self.transcribed_text += chunk_text[0] + "\n"  # Append the result
                except sr.UnknownValueError as e:
                    self.transcribed_text += "error transcribing segment" + "\n"
                except sr.RequestError as e:
                    self.transcribed_text += f"[Error with recognition: {str(e)}]" + "\n"

            # Update the progress label with each chunk's result
            self.progress_label.config(text=f"Processed {start_ms // chunk_duration + 1} chunks...")

        # Final updates after processing all chunks
        self.progress_label.config(text="Conversion Complete!")
        self.download_button.config(state="normal")

    def download_file(self):
        try:
            # Prompt the user to save the transcribed text file
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if save_path:
                # Save the transcribed text to the file
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(self.transcribed_text)
                messagebox.showinfo("Success", "Text file downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save the file: {str(e)}")


# Create the Tkinter root window
root = tk.Tk()
app = SpeechToTextApp(root)
root.mainloop()
