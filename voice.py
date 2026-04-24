from gtts import gTTS

def generate_voice(text, filename="output.mp3"):
    ad = gTTS(text=text, lang='en')
    ad.save(filename)
    return filename