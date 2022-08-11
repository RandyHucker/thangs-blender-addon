import threading
import time
import requests
from urllib.request import urlopen
import urllib.request
import urllib.parse
import importlib
import threading
import os
import math
import time
import bpy
from bpy.types import WindowManager
import bpy.utils.previews
from bpy.types import (Panel,
                       PropertyGroup,
                       Operator,
                       )
from bpy.props import (StringProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       )
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.app.handlers import persistent


class ThangsFetcher():
    def __init__(self, callback=None):
        self.thumbnails = []
        self.context = ""
        self.thangs_ui_mode = ''
        self.modelIds = []
        self.modelTitles = []
        self.filePaths = []
        self.modelInfo = []
        self.enumItems = []
        self.totalModels = 0
        self.Counter = 0
        self.pcoll = ""
        self.PageNumber = 1
        self.Directory = ""
        self.PageTotal = 0
        self.preview_collections = {}
        self.CurrentPage = 1
        self.searching = False
        self.failed = False
        self.query = ""
        self.deviceId = ""
        self.ampURL = 'https://production-api.thangs.com/system/events'
        self.search_thread = None
        self.heart_thread = None
        self.search_callback = callback
        pass

    def search(self, query):
        if self.searching:
            return False
        self.query = urllib.parse.quote(query)
        # this should return immediately with True
        # kick off a thread that does the searching
        self.search_thread = threading.Thread(
            target=self.get_http_search).start()

        # if self.search_callback is not None:
        #     self.search_callback()

        return True

    def cancel(self):
        if self.search_thread is not None:
            self.search_thread.terminate()
            self.search_thread = None
            self.searching = False
            self.reset
            return True
        return False

    def reset(self):
        self.thumbnails = []
        self.modelIds = []
        self.modelTitles = []
        self.filePaths = []
        self.modelInfo = []
        self.enumItems = []
        self.totalModels = 0
        self.Counter = 0
        self.pcoll = ""
        self.icons_dict = ""
        self.PageNumber = 1
        self.Directory = ""
        self.PageTotal = 0
        self.preview_collections = {}
        self.icon_collections = {}
        self.icons_dict
        self.CurrentPage = 1
        self.searching = False
        self.query = ""
        self.search_thread = None
        pass

    def makeheartbeat(self):
        self.heart_thread = threading.Thread(
            target=self.heartbeat).start()
        return

    def heartbeat(self):
        starttime = time.time()
        while True:
            print("Heartbeat")
            blenderAddonHeart = {
                "events": [
                    {
                        "event_type": "thangs-breeze - addon heartbeat",
                        "device_id": str(self.deviceId)
                    }
                ]
            }
            postResponse = requests.post(self.ampURL, json=blenderAddonHeart)
            time.sleep(600.0 - ((time.time() - starttime) % 600.0))

    def get_total_results(self):
        response = requests.get(
            "https://thangs.com/api/models/v2/search-by-text?utm_source=blender&utm_medium=referral&utm_campaign=blender_extender&searchTerm="+self.query+"&fileTypes=stl%2Cgltf%2Cobj%2Cfbx%2Cglb%2Csldprt%2Cstep%2Cmtl%2Cdxf%2Cstp&scope=thangs")
        if response.status_code != 200:
            self.totalModels = 0
            self.PageTotal = 0
        else:
            print("started counting results")
            responseData = response.json()
            items = responseData["results"]
            self.totalModels = len(items)
            self.PageTotal = math.ceil(self.totalModels/8)

            blenderSearchResults = {
                "events": [
                    {
                        "event_type": "thangs-breeze - search results",
                        "device_id": str(self.deviceId),
                        "event_properties": {
                            "number_of_results": str(self.totalModels)
                        }
                    }
                ]
            }
            postResponse = requests.post(
                self.ampURL, json=blenderSearchResults)

    def get_http_search(self):
        print("started Search")
        self.searching = True

        self.Directory = self.query
        # Added
        self.CurrentPage = self.PageNumber

        # Get the preview collection (defined in register func).

        self.pcoll = self.preview_collections["main"]

        if self.CurrentPage == self.pcoll.Model_page:
            if self.Directory == self.pcoll.Model_dir:
                self.searching = False
                self.search_callback()
                return
            else:
                self.get_total_results()
                self.PageNumber = 1
                self.CurrentPage = 1

        if self.Directory == "" or self.Directory.isspace():
            self.searching = False
            self.search_callback()
            return

        self.thumbnails.clear()
        self.modelIds.clear()
        self.modelTitles.clear()
        self.filePaths.clear()
        self.modelInfo.clear()
        self.enumItems.clear()

        self.Directory = self.query
        # Added
        self.CurrentPage = self.PageNumber

        # Get the preview collection (defined in register func).

        self.pcoll = self.preview_collections["main"]

        # Added

        for pcoll in self.preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        self.preview_collections.clear()

        self.pcoll = bpy.utils.previews.new()
        self.pcoll.Model_dir = ""
        self.pcoll.Model = ()
        self.pcoll.Model_page = self.CurrentPage

        self.preview_collections["main"] = self.pcoll

        self.pcoll = self.preview_collections["main"]

        blenderSearchStarted = {
            "events": [
                {
                    "event_type": "thangs-breeze - search started",
                    "device_id": str(self.deviceId),
                    "event_properties": {
                        "searchTerm": str(self.query)
                    }
                }
            ]
        }

        postResponse = requests.post(self.ampURL, json=blenderSearchStarted)
        # Come back and add in what to do if getting something besides a 200 response code

        self.failed = False

        response = requests.get(
            "https://thangs.com/api/models/v2/search-by-text?page="+str(self.CurrentPage-1)+"&searchTerm="+self.query+"&pageSize=8&narrow=false&collapse=true&fileTypes=stl%2Cgltf%2Cobj%2Cfbx%2Cglb%2Csldprt%2Cstep%2Cmtl%2Cdxf%2Cstp&scope=thangs")

        if response.status_code != 200:
            print("search failed")

            blenderSearchFailed = {
                "events": [
                    {
                        "event_type": "thangs-breeze - search failed",
                        "device_id": str(self.deviceId)
                    }
                ]
            }
            postResponse = requests.post(self.ampURL, json=blenderSearchFailed)

            self.failed = True

        else:
            responseData = response.json()
            items = responseData["results"]  # Each model result is X

            for item in items:
                print("Getting Item")
                thumbnailAPIURL = item["thumbnailUrl"]
                thumbnailURL = requests.head(thumbnailAPIURL)
                thumbnail = thumbnailURL.headers["Location"]
                self.thumbnails.append(thumbnail)
                modelId = item["modelId"]
                self.modelIds.append(modelId)

                modelTitle = item["modelTitle"]
                self.modelTitles.append(modelTitle)
                product_url = item["attributionUrl"]

                thumbnail = thumbnail.replace("https", "http", 1)

                filePath = urllib.request.urlretrieve(thumbnail)
                self.filePaths.append(filePath[0])

                self.modelInfo.append(
                    tuple([modelTitle, product_url, modelId]))

        self.Counter = 0
        for i, filePath in enumerate(self.filePaths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(self.modelIds[i], filePath)

            if self.modelTitles[i] in filepath:
                self.enumItems.append(
                    (self.modelTitles[i], self.modelIds[i], "", thumb.icon_id, i))
            else:
                thumb = self.pcoll.load(
                    self.modelIds[i], filepath, 'IMAGE')

            self.enumItems.append(
                (self.modelTitles[i], self.modelIds[i], "", thumb.icon_id, i))

            self.Counter = self.Counter + 1

        self.pcoll.Model = self.enumItems
        self.pcoll.Model_dir = self.Directory
        # Added
        self.pcoll.Model_page = self.CurrentPage

        self.searching = False

        self.thangs_ui_mode = 'VIEW'

        print("Callback")
        if self.search_callback is not None:
            self.search_callback()

        print("search completed")

        blenderSearchEnded = {
            "events": [
                {
                    "event_type": "thangs-breeze - search ended",
                    "device_id": str(self.deviceId)
                }
            ]
        }

        postResponse = requests.post(self.ampURL, json=blenderSearchEnded)

        return


# if __name__ == "__main__":
#     tf = ThangsFetcher()
#     tf.CurrentPage = 2
#     tf.search("cat")
#     while tf.searching:
#         print("searching...")
#         time.sleep(1)
#     for x in range(len(tf.modelInfo)):
#         print("results:", tf.modelInfo[x][0])
#     print(tf.modelTitles)
#     print(len(tf.modelTitles))
#     # print("https://thangs.com/api/models/v2/search-by-text?page="+str(tf.CurrentPage-1) +
#     #      "&searchTerm="+tf.query+"&pageSize=8&narrow=false&collapse=true&scope=thangs")
