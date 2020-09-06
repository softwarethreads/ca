import pprint

import requests


class Ingestor:
    def __init__(self):
        self.authorization = "s9-22d67f9d-a87e-464e-a0c1-ed5e2c4c657b"
        self.pp = pprint.PrettyPrinter(indent=4)

    def callWebservice(self, zipcode):
        print("Calling web service for zip", zipcode)
        url = 'https://slipstream.homejunction.com/ws/listings/search?market=hjimls&address.zip='+str(zipcode)+'&listingType=residential&details=true&sortField=listingDate&sortorder=desc&authorization='+str(self.authorization)
        #print(url)
        resp = requests.get(url)
        if resp.status_code != 200:
            # This means something went wrong.
            raise Exception('GET /tasks/ {}'.format(resp.status_code))
        #self.pp.pprint(resp.text)
        return resp

# ingestor = Ingestor()
# resp=ingestor.callWebservice("93505")
# ingestor.pp.pprint(resp.text)



