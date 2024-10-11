import streamlit as st
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

import os
from pathlib import Path
import re

import openai

base_path = Path("__file__").parent

st.set_page_config(page_title ="🐶🐶Text Generator App")
st.title('🐶🐶Text Generator App')
st.logo(image="./image/dog.png", size="medium", link=None, icon_image=None)
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

def generate_text(language_name="English", topic="Foods", num_sentences=5, level="Beginner"):
  ASSISTANT = "assistant:"
  llm = ChatMessage(model='gpt-4o-mini',
                   temperature=0.8,
                   max_tokens=None,
                   timeout=None,
                   max_retries=2,
                   openai_api_key=openai_api_key)
  template = '''
              I will make a shadowing practice app for {language_name} Language Learners.
              In shadowing practice, a teacher (may be a computer) reads a {language_name} sentence by sentence aloud, and learners repeat at the same pace, with a slight delay if possible.
              
              As for the {language_name} materials, generate {language_name} text for {language_name} Language Learners.
                -- Topic: {topic}
                -- Number of the sentences: Approx. {num_sentences}                
                -- Skill level: {level}, defined by the Common European Framework of Reference for Languages (CEFR)
              Just the text. No words needed.
              No numbering at the beginning of the sentences.
              Enclose each sentence in p tag.
              '''
              # *****
              # The first sentence of the text is the title.
              # That has no period, comma, punctuation, single quote, double quote, colon, semicolon and apostrophe.
              # And a space in the title is replaced by underscore.

  qa_template = PromptTemplate(template)
  prompt = qa_template.format(language_name=language_name, topic=topic, num_sentences=num_sentences, level=level)
  messages = [
              ChatMessage(role="system", content="You're a text generator that a user wants. No talks."),
              ChatMessage(role="user", content=prompt)
            ]
  res_text = OpenAI().chat(messages)
  return str(res_text).replace(ASSISTANT, "").strip()


def create_path(base_path:str, dir_name:str="temp"):
  path_joined = os.path.join(base_path, dir_name)
  try:
    if not os.path.exists(path_joined):
      os.makedirs(path_joined)
  except OSError:
    print("Error: Creating directory. " + path_joined)
  return path_joined


def create_speech(input:str, speed:int=1):
  """
  Create speech with TTS model.
  This function is for one sentence.
  """
  with openai.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="nova", #'nova', 'shimmer', 'echo', 'onyx', 'fable' or 'alloy'
    input=input,
    speed=speed,
  ) as response:
    return response

file_save_path = Path("__file__").parent / "rec"

with st.form('Foreign Language Sentence Generator'):
  language_name = st.selectbox(
    "What Languages do you learn? :",
    # ("Afrikaans", "Arabic", "Armenian", "Azerbaijani", "Belarusian", "Bosnian", "Bulgarian", "Catalan", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Finnish", "French", "Galician", "German", "Greek", "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Italian", "Japanese", "Kannada", "Kazakh", "Korean", "Latvian", "Lithuanian", "Macedonian", "Malay", "Marathi", "Maori", "Nepali", "Norwegian", "Persian", "Polish", "Portuguese", "Romanian", "Russian", "Serbian", "Slovak", "Slovenian", "Spanish", "Swahili", "Swedish", "Tagalog", "Tamil", "Thai", "Turkish", "Ukrainian", "Urdu", "Vietnamese", "Welsh"),
      ("Chinese", "English", "French", "German", "Italian", "Spanish"),
  )
  topic_text = st.text_input('What topics interest you? :', 'Foods')
  num_sentences = st.selectbox(
    "How many sentences do you read aloud? :", ("3", "5", "10", "15", "20")
  )
  level = st.selectbox(
    "Your skill level:",
    ("Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced", "Proficiency"),
  )

  rec_activated = st.toggle('Activate REC mode')
  
  submitted = st.form_submit_button('Submit')
  if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    st.divider()
    text = generate_text(language_name, topic_text, num_sentences, level)
    st.html(text)
    sentences = []
    sentences = re.findall('<p>(.*?)</p>', text)

    # if rec_activated:
    #   st.experimental_audio_input("Record your practice")
    for i, s in enumerate(sentences):
      # Extract a title from the first sentence.
      if i == 0:
        title = s
        print(f"{title=}")
        file_save_path = create_path(file_save_path, title)
        continue
      # res = create_speech(s)
      with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="nova", #'nova', 'shimmer', 'echo', 'onyx', 'fable' or 'alloy'
        input=s,
        speed=1,
      ) as response:
        try:
          response.stream_to_file(f"{file_save_path}/{title}_{i}_.mp3")
        except Exception as e:
          st.error(e)
 