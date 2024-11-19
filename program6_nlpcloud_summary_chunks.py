import base64
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import nlpcloud
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
        self.transcribed_text = None
        self.export_path = "transcribed_text.txt"

    def upload_file(self):
        self.wav_file = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav"), ("MP3 files", "*.mp3")])
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

    # 05587183042d894bb3232047c1333cd62b65a6ab
    def process_file(self):

        token = '87097ac1296672b24f2d6ca902cb88af937f2c53'
        self.progress_label.config(text="Processing... Please wait.")
        client = nlpcloud.Client("whisper", token, True)

        # Load the audio file using pydub
        audio = AudioSegment.from_wav(self.wav_file)
        total_duration = len(audio)  # in milliseconds
        chunk_duration = 120 * 1000  # 5 seconds in milliseconds
        self.transcribed_text = ""

        # Process the audio in 5-second chunks
        for start_ms in range(0, total_duration, chunk_duration):
            end_ms = min(start_ms + chunk_duration, total_duration)
            chunk = audio[start_ms:end_ms]

            # Export the chunk to a temporary file for recognition
            chunk_path = "temp_chunk.wav"
            chunk.export(chunk_path, format="wav")
            chunk_number = f"Transcribing chunk {start_ms // chunk_duration + 1}..."
            # Update UI progress
            self.progress_label.config(text=chunk_number)
            with open(chunk_path, 'rb') as binary_file:
                binary_file_data = binary_file.read()
                base64_encoded_data = base64.b64encode(binary_file_data)
                base64_output = base64_encoded_data.decode('utf-8')
                print(base64_output)

                try:
                    result = client.asr(encoded_file=base64_output, input_language='ar')
                    self.transcribed_text += result["text"] + ' '
                except Exception:
                    self.transcribed_text += f"\nError transcribing chunk f{chunk_number}\n"

        # Summarize the transcribed text using the Finetuned LLaMA-3-70B model
        summary_client = nlpcloud.Client("finetuned-llama-3-70b", token, gpu=True)
        try:
            summarized_content = summary_client.summarization(text=self.transcribed_text)
            self.transcribed_text += '\n\n\n\n' + summarized_content["summary_text"]
        except Exception:
            self.transcribed_text += f"\nError summarizing text\n"

        # Update the UI with the result
        self.progress_label.config(text="Conversion Complete!")
        self.download_button.config(state="normal")

    def download_file(self):
        self.progress_label.config(text=self.transcribed_text)
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
