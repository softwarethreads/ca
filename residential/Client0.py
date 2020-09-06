import requests
import time
import speech_recognition as sr
import logging
import pprint


class Client:

    def __init__(self):
        self.API_ENDPOINT = "http://localhost:9000"
        self.pp = pprint.PrettyPrinter(indent=4)

    def post(self, question):
        # data to be sent to api
        try:
            data = {'query': question}
            logging.info(data)
            r = requests.post(url=self.API_ENDPOINT, json=data)
            status = r.status_code
            logging.info("content="+str(r.content))
            logging.info("status="+str(status))
            return r.content
        except Exception as ex:
            print(str(ex))

    def get(self):
        try:
            PARAMS = {'address': 'foo'}
            r = requests.get(url=self.API_ENDPOINT, params=PARAMS)
            data = r.json()
            logging.info(data)
        except Exception as ex:
            print(str(ex))

    def recognize_speech_from_mic(self, recognizer, microphone):
        """Transcribe speech from recorded from `microphone`.

        Returns a dictionary with three keys:
        "success": a boolean indicating whether or not the API request was
                   successful
        "error":   `None` if no error occured, otherwise a string containing
                   an error message if the API could not be reached or
                   speech was unrecognizable
        "transcription": `None` if speech could not be transcribed,
                   otherwise a string containing the transcribed text
        """
        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            response["transcription"] = recognizer.recognize_google(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"
        return response

    def commandLine(self):

        question = "download zip 93505"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "set default zip to 93505"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "get default zip"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "what properties are on the market in the price range 100,000 to 300000"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)
        #    i = i+1
        question = "make 69965 Rosemary Court the default house"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "what is the price of the house"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "how many bedrooms and bathrooms does it have"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "how long has the property been on the market"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "How much section 1 work does the house have"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

        question = "what is the required setback from lot boundary"
        print("user:", question)
        response = client.post(question)
        response_str = response.decode('utf-8')
        print("dsiva:", response_str)

    def getQuestion(self) :
        try:
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            print('please ask a question, say exit to quit')
            time.sleep(3)
            guess = self.recognize_speech_from_mic(recognizer, microphone)
            if not guess["transcription"] or not guess["success"]:
                print("I didn't catch that. What did you say?\n")
            if guess["error"]:
                logging.info("ERROR: {}".format(guess["error"]))
            if guess["transcription"]:
                print("You said: {}".format(guess["transcription"]))
            if guess["transcription"] == "exit":
                print("Exiting...")
                exit()
            if guess["transcription"]:
                question = guess["transcription"].lower()
                return question
        except Exception as ex:
            print(str(ex))


client = Client()
print("Welcome to DSIVA")
client.commandLine()

