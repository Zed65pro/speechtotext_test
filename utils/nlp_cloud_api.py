import base64
import os

import nlpcloud

finetuned_llama_client = nlpcloud.Client("finetuned-llama-3-70b", os.getenv("NLPCLOUD_TOKEN"),
                                         gpu=True)  # Using fine-tuned-llma-3-70b because it supports arabic
whisper_client = nlpcloud.Client("whisper", os.getenv("NLPCLOUD_TOKEN"), True)


class NLPCloudApi:
    @classmethod
    def generate_analysis_for_conversation(cls, conversation_text):
        result = finetuned_llama_client.generation(conversation_text, max_length=8000)
        return result['generated_text']

    @classmethod
    def generate_speech_to_text_from_local_file(cls, file_path, ):
        with open(file_path, 'rb') as binary_file:
            binary_file_data = binary_file.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            base64_output = base64_encoded_data.decode('utf-8')

            asr_result = whisper_client.asr(encoded_file=base64_output, input_language='ar')
            return asr_result["text"]

    @classmethod
    def correct_grammar_from_text(cls, text):
        grammar_correction_result = finetuned_llama_client.gs_correction(text=text)
        return grammar_correction_result['correction']

    @classmethod
    def generate_summary_from_text(clscls, text):
        summary_result = finetuned_llama_client.summarization(text=text)
        return summary_result["summary_text"]
