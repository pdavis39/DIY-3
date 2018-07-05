#
# author: Paul Davis
# email: pdavis39@gmail.com
# created: 2/29/2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import json
import requests
import time
import websockets
import asyncio 
import ast

# variables
#events = ''

try:
    while True:

        # read event
        @asyncio.coroutine
        def eventListen():
            websocket = yield from websockets.connect('ws://<URL>:3000/')

            try:
                eventsListen = yield from websocket.recv()

                events = eventsListen

                events = ast.literal_eval(events)

                asset = events['asset']

                objectState = events['objectState']

                noteU = "Ticket 123 has been opened by Analyst Hank Williams to improve classifier results against " + asset
                noteT = "Hank reviewed the results and no action is required to update the image classifier " + asset

                if objectState == "UNKNOWN":
                    print("The analyst does some off-chain process based on the contents of the Hyperledger emitting an event")
                    time.sleep(1)
                    print("The analyst does some off-chain process based on the contents of the Hyperledger emitting an event")

                    url = "http://<URL>:3000/api/com.diy3.QaTransaction"


                    payload = "{\n   \"$class\": \"com.diy3.QaTransaction\", \n   \"asset\": "'"'+asset+'"'",  \n   \"analyst\": \"resource:com.diy3.Analyst#4652\",\n   \"note\": "'"'+noteU+'"'" }"

                    headers = {'Content-Type': "application/json",'Cache-Control': "no-cache",}

                    #response = response = requests.post(url = url, data=payload, headers=headers)
                    response = requests.request("POST", url, data=payload, headers=headers)
                    print(response.text)
                    #print(json.dumps(response, indent=4, sort_keys=True))
                    print("sent transaction to composer-rest-server")
                    print("ready for the next event")
                if objectState == "SPORTS_ITEM":
                    print("The analyst does some off-chain process based on the contents of the Hyperledger emitting an event")
                    time.sleep(1)
                    print("The analyst does some off-chain process based on the contents of the Hyperledger emitting an event")

                    url = "http://<URL>:3000/api/com.diy3.QaTransaction"


                    payload = "{\n   \"$class\": \"com.diy3.QaTransaction\", \n   \"asset\": "'"'+asset+'"'",  \n   \"analyst\": \"resource:com.diy3.Analyst#4652\",\n   \"note\": "'"'+noteT+'"'" }"

                    headers = {'Content-Type': "application/json",'Cache-Control': "no-cache",}

                    #response = response = requests.post(url = url, data=payload, headers=headers)
                    response = requests.request("POST", url, data=payload, headers=headers)
                    print(response.text)
                    #print(json.dumps(response, indent=4, sort_keys=True))
                    print("sent transaction to composer-rest-server")
                    print("ready for the next event")

            finally:
                yield from websocket.close()
                #print('next transaction')

        asyncio.get_event_loop().run_until_complete(eventListen())
        #asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    print('interrupted!')
