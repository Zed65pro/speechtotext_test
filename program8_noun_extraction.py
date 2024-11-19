import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from dotenv import load_dotenv
import os
from sinatools.morphology import morph_analyzer


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

    def process_file(self):
        load_dotenv()
        token = os.getenv("NLPCLOUD_TOKEN")

        self.progress_label.config(text="Processing... Please wait.")
        self.transcribed_text = ''
        # text = 'أعلنت وزارة المالية في فلسطين عن تخفيض ضريبة الدخل في الضفة الغربية وقطاع غزة'
        text = 'النقاش يتناول مشكلة في اتصال جهاز المدى تي في، حيث يتحدث المتلقي مع فني دعم حول عدم تشغيل الجهاز. تم إرشاده للتحقق من كابل الإيثيرنت والتأكد من توصيله بشكل صحيح بين الراوتر والرسيفر. بعد عدة محاولات، تأكد الفني من أن الإتصال يعمل بشكل سليم وأن المشكلة كانت في الكابل أو مدخل الرسيفر. في النهاية، تم حل المشكلة بإعادة تشغيل الإعدادات'
        try:
            nouns = morph_analyzer.analyze(text=text)
            # nouns = disambiguate(sentence=text.strip().replace(',', '').replace('.', ''))
            # self.transcribed_text += '\n\n\n\n' + nouns
        except Exception as e:
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
