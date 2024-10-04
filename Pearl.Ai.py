#necessary modules
import os
from playsound import playsound
from openai import OpenAI #openAI API module
import speech_recognition as sr #speech recognition module
import datetime
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import urllib.request
import os


#fetch api key from env variables
API_KEY = os.getenv('API_KEY')
if API_KEY is None:
    print("API key not found. Please set the API_KEY environment variable.")
else:
    # Use the API key in your application
    print(f"API Key: {API_KEY}")



#api key
client= OpenAI(api_key=API_KEY)


#initialize recognition instance, recognizes speech
def listen():
    # used from an old program 
    recognition = sr.Recognizer()
    max_tokens = 200
    with sr.Microphone(device_index=1) as source: 
        audio = recognition.listen(source)
        said = ''

    said = recognition.recognize_google(audio)

    return audio

#handling wav data source:https://docs.python.org/3/library/wave.html
def make_file(audio):
    with open ('user_audiodata.wav','wb') as file: 
        wav_data = audio.get_wav_data()
        file.write(wav_data)
    
    audio_file = open(os.path.abspath('user_audiodata.wav'),'rb')
    return audio_file


#sources openai api:  https://platform.openai.com/examples,https://platform.openai.com/docs/guides/text-to-speech
def translate_to_english(audio_file, input_lang):
    prompt = f'the language of the audio file is  in {input_lang} . Your response should be in the language English'
    transcript = client.audio.translations.create(
        model = "whisper-1",
        prompt= prompt,
        file = audio_file,
        response_format='text',
        temperature= 0.2
        
    )
    return transcript

def translate_to_non_english(text, output_lang):
    completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
    {"role": "system", "content": "You are a detail oriented translation assistant. The input must be correctly translated to specific output"},
    {"role": "user", "content": f"translate {text} to {output_lang}."}

  ] 
)
    return completion.choices[0].message
#sources openai api:  https://platform.openai.com/examples,https://platform.openai.com/docs/guides/speech-to-text
def speech_to_text(audio_file):
    transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="text"
)
    


    return transcript


#sources openai api:  https://platform.openai.com/examples,https://platform.openai.com/docs/guides/text-to-speech
def text_to_speech(transcript):
    print(f'Transcript data type: {type(transcript)}')
    transcript = str(transcript)
    response = client.audio.speech.create(
        model='tts-1',
        voice ='shimmer',
        input=transcript
    )

    with open ('output.mp3', 'wb') as file:
        file.write(response.content)
    


#documentation from opeai and Daniels GPT url:https://platform.openai.com/examples

def generate_dalle_image_from_text(transcript, input_lang,output_lang,value):
    if value == None: 
        value = 'No'
    if len(input_lang)==0 or len(output_lang)==0:
            
            print('languages were len 0')


            prompt = f'''you are a tool for creating visual representations of language for a 
            language translation app. draw a visual representation of people speaking in different languages
            Output only the translations. do not output any other uneccessary text.
            '''

            response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size = '1024x1024',
            quality = 'standard',
            n = 1
        )
            display_image(response.data[0].url)
    else: 
        print('else statement works')
        if value == 'Yes': 
            print('the value was yes')
              # Generate image using DALL-E
            prompt = f'''you are a tool for creating visual representations of language for a language translation app. draw a visual representation of someone saying  {transcript} in {input_lang}
                and someone reading the translation in {output_lang}'''
            response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size = '1024x1024',
            quality = 'standard',
            n = 1
        )
            print(response.data[0].url)
            display_image(response.data[0].url)
        else: 
            return ''
    
#tkinter article source: https://www.tutorialspoint.com/displaying-images-from-url-in-tkinter
def display_image (url):
        image_window = tk.Toplevel()
        urllib.request.urlretrieve(url,"generated_image.jpg")
        image = Image.open('generated_image.jpg')
        generated_image = ImageTk.PhotoImage(image)
        gen_image_label = tk.Label(image_window,image=generated_image)
        gen_image_label.pack()
        image_window.mainloop()

    

def play_speech():
    playsound('output.mp3')
    
    


def entry(transcript, translation, timestamp, first_name, last_name): 
    entry = {'TRANSCRIPTION': transcript, 'TRANSLATION': translation, 'TIMESTAMP': timestamp, 'FIRST NAME': first_name, 'LAST NAME': last_name}
    return entry


def conversation_data (entry, conversation_df): 
    return pd.concat([conversation_df, pd.DataFrame([entry])], ignore_index=True)


def save_current_data(conversation_df):
    conversation_df.to_csv('PEARL_CONVERSATION_DATA.csv', index=False)



def load_conversation_data():
    if os.path.exists('PEARL_CONVERSATION_DATA.csv'):
        return pd.read_csv('PEARL_CONVERSATION_DATA.csv')
    else: 
        return pd.DataFrame(columns=['TRANSCRIPTION','TRANSLATION', 'TIMESTAMP', 'FIRST NAME','LAST NAME'])



def load_user_data():
    if os.path.exists('USER_INFO.csv'):
        return pd.read_csv('USER_INFO.csv')
    else: 
        return pd.DataFrame(columns=['First Name','Last Name','Birthday','Language'])
    



def retrieve_user_info(root, first_name: str, last_name: str):
    user_info_df = pd.read_csv('USER_INFO.csv')
    matched_rows = []
    for index, row in user_info_df.iterrows():
        if str(row['First Name']).strip().lower() == str(first_name).strip().lower() and str(row['Last Name']).strip().lower() == str(last_name).strip().lower():
            matched_rows.append(row)
    if matched_rows:
        messagebox.showinfo('User Info', pd.DataFrame(matched_rows).to_string(index=False))
    else: 
        messagebox.showinfo('User Not Found', pd.DataFrame(user_info_df).to_string(index=False))


    

def retrieve_conversation_info(root, first_name:str, last_name:str):
    conversation_df = pd.read_csv('PEARL_CONVERSATION_DATA.csv')
    matched_rows = conversation_df[(conversation_df['FIRST NAME'].str.lower() == first_name.lower()) & (conversation_df['LAST NAME'].str.lower() == last_name.lower())]
    if not matched_rows.empty:
        messagebox.showinfo('Conversation Entries', matched_rows.to_string(index=False))
    else:
        messagebox.showinfo('User Not Found', 'No conversation data found for this user.')



#iterating over rows source: https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-pandas-dataframe
#tkinter sources:https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-pandas-dataframe,
def start_conversation(root,status_label,transcript_text,aitranscript_text, input_lang, output_lang,first_name,last_name,image_choice_var):

    if os.path.exists("output.mp3"):
        os.remove("output.mp3")
    #check for an existing user
    user_info = load_user_data()
    user_data = pd.DataFrame()



    for index, row in user_info.iterrows():
        if str(row['First Name']).strip().lower() == first_name.strip().lower() and str(row['Last Name']).strip().lower() == last_name.strip().lower():
            user_data = pd.DataFrame(row)
    if user_data.empty: 
        user_data = user_info
    elif not user_data.empty: 
        user_data = pd.DataFrame(row).to_string(index=False)
    else:
        messagebox.showinfo('User Not Found', 'Please enter user Details')

    

    status_label.config(text= "Listening...")
    root.update_idletasks()

    audio = listen()
    audio_file = make_file(audio)
    transcript = speech_to_text(audio_file)


    #determine which translation functions to use
    if input_lang == 'English' and output_lang != 'English':
        translation = translate_to_non_english(transcript, output_lang)
        translation = translation.content
    elif input_lang!= 'English' and output_lang =='English':
        translation = translate_to_english(audio_file,input_lang)
    else: 
        to_english = translate_to_english(audio_file,input_lang)
        translation = translate_to_non_english(to_english, output_lang)
        translation = translation.content



    print(translation)

    #get time
    time = datetime.datetime.now()
    

    
    text_to_speech(translation)
    speech_entry = entry(transcript,translation, user_data, first_name, last_name)
    conversation_df = load_conversation_data()
    user_info_str = user_data
    conversation_df = conversation_data(speech_entry, conversation_df)
    save_current_data(conversation_df)
    print(speech_entry)
    
    
    transcript_text.delete('1.0',tk.END)
    transcript_text.insert(tk.END, transcript)

     
    aitranscript_text.delete('1.0', tk.END)
    aitranscript_text.insert(tk.END, translation)


    status_label.config(text= "Finished")

     
    generate_dalle_image_from_text(transcript, input_lang, output_lang, image_choice_var)

    


def save_user_info(first_name, last_name, day_var, month_var, year_var, language_var ):
    
    first_name = first_name.get()
    last_name = last_name.get()
    birthday = f"{month_var.get()}/{day_var.get()}/{year_var.get()}"
    language = language_var.get()

   
    user_info_df = pd.DataFrame({
        'First Name': [first_name],
        'Last Name': [last_name],
        'Birthday': [birthday],
        'Language': [language]
    })

   
    if os.path.exists('USER_INFO.csv'):
        user_info_df.to_csv('USER_INFO.csv', mode='a', header=False, index=False)
    else:
        user_info_df.to_csv('USER_INFO.csv', index=False)

    messagebox.showinfo('Success','User Details Saved!')




def application_info ():
    introduction ='''Welcome to Pearl.AI. AI powered language translation application and database.
    1. The user details frame allows you to enter your information if you are new\n
    2. The translation frame in the top right prompts you with language input and output (optional),
     entries to put user information (optional), and weather or not youd like\n
    3. The default is to translate whatever you say into
     multiple different languages and output the transcript.\n
    4. You also have the option to playback the audio of the translation
       a visual represenation of the exchange\n
    5. The retrieve conversation data or user data frame allows you to access both user and conversation data sets given an users first and last name.
    The default is outputting all values if it is empty or the names are not found.\n
    '''
    messagebox.showinfo('Pearl.AI- Program Information',introduction)


#tikiner sources continued: https://www.askpython.com/python-modules/tkinter/drawing-lines,https://www.geeksforgeeks.org/python-tkinter-entry-widget/,
#https://pythonassets.com/posts/drop-down-list-combobox-in-tk-tkinter/,https://www.pythontutorial.net/tkinter/tkinter-combobox/
def main():
    application_info()
    conversation_df = load_conversation_data()
    root = tk.Tk()
    root.title('Pearl.AI')
    root.geometry('700x700')
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    #user details frame
    user_details_frame = tk.Frame(root, padx=0, pady=0, relief='ridge', borderwidth=4)
    user_details_frame.grid(row=0, column=0, padx=0, pady=0, sticky='nesw')

    #user input for user database
    user_input_menu = tk.Label(user_details_frame, text='Please enter your details:')
    user_input_menu.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='n')

    #first name entry
    first_name_label = tk.Label(user_details_frame, text="First Name:")
    first_name_label.grid(row=1, column=0, padx=10, pady=5)
    first_name_entry = tk.Entry(user_details_frame)
    first_name_entry.grid(row=1, column=1, padx=10, pady=5)

    #Last name entry
    last_name_label = tk.Label(user_details_frame, text="Last Name:")
    last_name_label.grid(row=2, column=0, padx=10, pady=5)
    last_name_entry = tk.Entry(user_details_frame)
    last_name_entry.grid(row=2, column=1, padx=10, pady=5)

    #dob details
    dob_label = tk.Label(user_details_frame, text='Birthday:')
    dob_label.grid(row=3, column=0, padx=1, pady=1)

    #month dropdown
    month_label = tk.Label(user_details_frame, text='Month:')
    month_label.grid(row=4, column=0, padx=1, pady=1)
    month_options = [i for i in range(1, 13)]
    month_var = tk.StringVar(user_details_frame)
    month_dropdown = ttk.Combobox(user_details_frame, textvariable=month_var, values=month_options, state='readonly', width=4)
    month_dropdown.grid(row=4, column=1, padx=2, pady=2)
    month_dropdown.set('MM')

    #day dropdown
    day_label = tk.Label(user_details_frame, text='Day:')
    day_label.grid(row=5, column=0, padx=1, pady=1)
    day_options = [i for i in range(1, 33)]
    day_var = tk.StringVar(user_details_frame)
    month_dropdown = ttk.Combobox(user_details_frame, textvariable=day_var, values=day_options, state='readonly', width=4)
    month_dropdown.grid(row=5, column=1, padx=2, pady=2)
    month_dropdown.set('DD')

    #year dropdown
    year_label = tk.Label(user_details_frame, text='Year:')
    year_label.grid(row=6, column=0, padx=1, pady=1)
    year_options = [i for i in range(1910, 2025)]
    year_var = tk.StringVar(user_details_frame)
    year_dropdown = ttk.Combobox(user_details_frame, textvariable=year_var, values=year_options, state='readonly', width=6)
    year_dropdown.grid(row=6, column=1, padx=2, pady=2)
    year_dropdown.set('YYYY')

    #native language dropdown
    language_options = [
        "Afrikaans", "Arabic", "Armenian", "Azerbaijani", "Belarusian", "Bosnian",
        "Bulgarian", "Catalan", "Chinese", "Croatian", "Czech", "Danish", "Dutch",
        "English", "Estonian", "Finnish", "French", "Galician", "German", "Greek",
        "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Italian",
        "Japanese", "Kannada", "Kazakh", "Korean", "Latvian", "Lithuanian",
        "Macedonian", "Malay", "Marathi", "Maori", "Nepali", "Norwegian", "Persian",
        "Polish", "Portuguese", "Romanian", "Russian", "Serbian", "Slovak", "Slovenian",
        "Spanish", "Swahili", "Swedish", "Tagalog", "Tamil", "Thai", "Turkish",
        "Ukrainian", "Urdu", "Vietnamese", "Welsh"
    ]

    language_label = tk.Label(user_details_frame, text='Native Language')
    language_label.grid(row=7, column=0, padx=1, pady=1)
    language_var = tk.StringVar(user_details_frame)
    language_dropdown = ttk.Combobox(user_details_frame, textvariable=language_var, values=language_options, state='readonly', width=10)
    language_dropdown.grid(row=7, column=1, padx=2, pady=2)
    language_dropdown.set('Languages')

    #enter user info button
    enter_button = tk.Button(user_details_frame, text='Enter', command=lambda: save_user_info(first_name_entry, last_name_entry, day_var, month_var, year_var, language_var), width=15)
    enter_button.grid(row=8, column=1, padx=10, pady=10)

    #divider
    divider = ttk.Separator(user_details_frame, orient='horizontal')
    divider.grid(row=9, column=0, columnspan=2, sticky='ew', pady=10)

    #retrieve data functions 
    data_functions_label = tk.Label(user_details_frame,text='Retrieve Conversation or User Data:')
    data_functions_label.grid(row=10,column=0,padx=2,pady=2)

    #fn label and entry
    fn_data_label = tk.Label(user_details_frame, text="First Name:")
    fn_data_label.grid(row=11, column=0, padx=5, pady=5, sticky='w')
    fn_data_entry = tk.Entry(user_details_frame)
    fn_data_entry.grid(row=12, column=1, padx=5, pady=5, sticky='w')


    #Last name entry
    ln_data_label = tk.Label(user_details_frame, text="Last Name:")
    ln_data_label.grid(row=13, column=0, padx=5, pady=5, sticky='w')
    ln_data_entry = tk.Entry(user_details_frame)
    ln_data_entry.grid(row=14, column=1, padx=5, pady=5, sticky='w')


    #buttons for convo or user data name entry
    #,command=retrieve_conversation_info(root, fn_data_entry.get(),ln_data_entry.get())
    user_info_btn = tk.Button(user_details_frame, text='User Data',command=lambda: retrieve_user_info(root, fn_data_entry.get(),ln_data_entry.get()))
    user_info_btn.grid(row=15, column=0, padx=5, pady=5)
    conversation_info_btn = tk.Button(user_details_frame, text='Conversation Data',command=lambda: retrieve_conversation_info(root, fn_data_entry.get(),ln_data_entry.get()))
    conversation_info_btn.grid(row=16, column=0, padx=5, pady=5)


    # app functions frame
    app_functions_frame = tk.Frame(root, padx=10, pady=10, relief='ridge', borderwidth=4)
    app_functions_frame.grid(row=0, column=1, padx=0, pady=0, sticky='nsew')

    # conversation functionality labels
    status_label = tk.Label(app_functions_frame, text='')
    status_label.grid(row=0, column=0, padx=1, pady=1)

    # input language drop down...
    input_lang_label = tk.Label(app_functions_frame, text='Input Language')
    input_lang_label.grid(row=1, column=0, padx=1, pady=1)
    input_lang_options = language_options
    input_lang_var = tk.StringVar(app_functions_frame)
    input_lang_dropdown = ttk.Combobox(app_functions_frame, textvariable=input_lang_var, values=input_lang_options, state='readonly', width=10)
    input_lang_dropdown.set('Languages')
    input_lang_dropdown.grid(row=2, column=0, padx=2, pady=2)


    # output language dropdown...
    output_lang_label = tk.Label(app_functions_frame, text='Output Language')
    output_lang_label.grid(row=3, column=0, padx=1, pady=1)
    output_lang_options = language_options
    output_lang_var = tk.StringVar(app_functions_frame)
    output_lang_dropdown = ttk.Combobox(app_functions_frame, textvariable=output_lang_var, values=output_lang_options, state='readonly', width=10)
    output_lang_dropdown.set('Languages')
    output_lang_dropdown.grid(row=4, column=0, padx=2, pady=2)

    # first name entry
    first_name_label = tk.Label(app_functions_frame, text="First Name:")
    first_name_label.grid(row=5, column=0, padx=5, pady=5)
    first_name_entry = tk.Entry(app_functions_frame)
    first_name_entry.grid(row=6, column=0, padx=5, pady=5)

    # Last name entry
    last_name_label = tk.Label(app_functions_frame, text="Last Name:")
    last_name_label.grid(row=7, column=0, padx=5, pady=5)
    last_name_entry = tk.Entry(app_functions_frame)
    last_name_entry.grid(row=8, column=0, padx=5, pady=5)


    #checkbox 
    image_choice_label = tk.Label(app_functions_frame,text='Generate an Image?')
    image_choice_label.grid(row=9,column=0,padx=1,pady=2)
    image_choice_var = tk.StringVar(app_functions_frame)
    image_choice_dropdown = ttk.Combobox(app_functions_frame,textvariable=image_choice_var,values=['Yes','No'],state='readonly',width=5)
    image_choice_dropdown.grid(row=10,column=0,padx=1,pady=1)

    
    # start conversation button
    start_button = tk.Button(app_functions_frame, text='Start Conversation', command=lambda: start_conversation(root, status_label, transcript_text, aitranscript_text, input_lang_var.get(), output_lang_var.get(), first_name_entry.get(), last_name_entry.get(), image_choice_var.get()))
    start_button.grid(row=11, column=0, padx=10, pady=10)

    # text user transcript
    transcript_text = tk.Text(app_functions_frame, height=5, width=39)
    transcript_text.grid(row=12, column=0, padx=10, pady=10)

    #AI translation
    aitranscript_text = tk.Text(app_functions_frame, height=5, width=39)
    aitranscript_text.grid(row=13, column=0, padx=10, pady=10)

    # play conversation button
    play_translation_button = tk.Button(app_functions_frame, text='Play Translation', command=play_speech)
    play_translation_button.grid(row=14, column=0, padx=10, pady=10)


    
    root.mainloop()
main()





