# this module contains the classes that represent the requests sent to the anki connect api
# in order to implement a new request, you need to create a class that implements the ToAnkiJson protocol
# the name of the class will be Anki{RequestName}Request
# and it will have a method to_anki_dict that returns a dictionary that represents the request.
# It should also have a __init__ method that accepts an object of the type that will be converted to the dictionary


from typing import Any, List, Protocol

from media import Picture
from notes.note import Note


class ToAnkiJson(Protocol):
    def to_anki_dict(self):
        pass


class AnkiAddNotesRequest:
    """
        ex:
        {
        "action": "addNotes",
        "version": 6,
        "params": {
            "notes": [
                {
                    "deckName": "Default",
                    "modelName": "Basic",
                    "fields": {
                        "Front": "front content",
                        "Back": "back content"
                    },
                    "tags": [
                        "yomichan"
                    ],
                    "audio": [{
                        "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=猫&kana=ねこ",
                        "filename": "yomichan_ねこ_猫.mp3",
                        "skipHash": "7e2c2f954ef6051373ba916f000168dc",
                        "fields": [
                            "Front"
                        ]
                    }],
                    "video": [{
                        "url": "https://cdn.videvo.net/videvo_files/video/free/2015-06/small_watermarked/Contador_Glam_preview.mp4",
                        "filename": "countdown.mp4",
                        "skipHash": "4117e8aab0d37534d9c8eac362388bbe",
                        "fields": [
                            "Back"
                        ]
                    }],
                    "picture": [{
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/A_black_cat_named_Tilly.jpg/220px-A_black_cat_named_Tilly.jpg",
                        "filename": "black_cat.jpg",
                        "skipHash": "8d6e4646dfae812bf39651b59d7429ce",
                        "fields": [
                            "Back"
                        ]
                    }]
                }
            ]
        }
    }
    becareful when setting the target deck, because if it does not exist, the adding procedure will fail because of ankiconnect.
    """

    notes: List[Note]

    def __init__(self, notes: List[Note]):
        self.action = "addNotes"
        self.version = 6
        self.params = {"notes": [note.to_anki_dict() for note in notes]}

    def to_anki_dict(self):
        return self.__dict__


class AnkiMultiRequest:
    """
        ex:
        {
        "action": "multi",
        "version": 6,
        "params": {
            "actions": [
                {
                    "action": "deckNames"
                },
                {
                    "action": "deckNames",
                    "version": 6
                },
                {
                    "action": "invalidAction",
                    "params": {"useless": "param"}
                },
                {
                    "action": "invalidAction",
                    "params": {"useless": "param"},
                    "version": 6
                }
            ]
        }
    }
    """

    notes: List[Any]

    def __init__(self, requests: List[Any]):
        self.action = "multi"
        self.version = 6
        self.requests = requests

    def to_anki_dict(self):
        return {
            "action": self.action,
            "version": self.version,
            "params": {
                "actions": [request.to_anki_dict() for request in self.requests]
            },
        }


class AnkiGetMediaFilesNamesRequest:
    """
    {
        "action": "getMediaFilesNames",
        "version": 6,
        "params": {
            "pattern": "_hell*.txt"
        }
    }
    """

    def __init__(self, pattern: str = None):
        self.action = "getMediaFilesNames"
        self.version = 6
        if pattern:
            self.params = {"pattern": pattern}

    def to_anki_dict(self):
        return self.__dict__


class AnkiRetrieveMediaFileRequest:
    """{
        "action": "retrieveMediaFile",
        "version": 6,
        "params": {
            "filename": "_hello.txt"
        }
    }"""

    def __init__(self, filename: str):
        self.action = "retrieveMediaFile"
        self.version = 6
        self.params = {"filename": filename}

    def to_anki_dict(self):
        return self.__dict__


class AnkiStoreMediaFileRequest:
    """
    {
        "action": "storeMediaFile",
        "version": 6,
        "params": {
            "filename": "_hello.txt",
            "data": "SGVsbG8sIHdvcmxkIQ=="
        }
    }
    """

    def __init__(self, picture: Picture):
        self.action = "storeMediaFile"
        self.version = 6
        self.params = {"filename": picture.filename, "data": picture.data}

    def to_anki_dict(self):
        return self.__dict__


class AnkiUpdateNoteRequest:
    """
        updates the fields and/or tags
        ex:
        {
        "action": "updateNote",
        "version": 6,
        "params": {
            "note": {
                "id": 1514547547030,
                "fields": {
                    "Front": "new front content",
                    "Back": "new back content"
                },
                "tags": ["new", "tags"]
            }
        }
    }
    """

    def __init__(self, note: Note):
        self.action = "updateNote"
        self.version = 6
        self.params = {"note": note.to_anki_dict()}

    def to_anki_dict(self):
        return self.__dict__


class AnkiFindNotesRequest:
    """
        ex:
        {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": "deck:Default"
        }
    }
    the query syntax is at https://docs.ankiweb.net/searching.html
    and an empty string returns all cards
    """

    def __init__(self, query: str = ""):
        self.action = "findNotes"
        self.version = 6
        self.params = {"query": query}

    def to_anki_dict(self):
        return self.__dict__


class AnkiChangeDeckRequest:
    """
        ex:
        {
        "action": "changeDeck",
        "version": 6,
        "params": {
            "cards": [1514547547030],
            "deck": "Default"
        }
    }
    """

    def __init__(self, note: Note):
        self.action = "changeDeck"
        self.version = 6
        self.params = {"cards": [note.id], "deck": note.target_deck}

    def to_anki_dict(self):
        return self.__dict__


class AnkiDeleteNotesRequest:
    """
        ex:
        {
        "action": "deleteNotes",
        "version": 6,
        "params": {
            "notes": [1514547547030]
        }
    }
    """

    def __init__(self, notes: List[Note]):
        self.action = "deleteNotes"
        self.version = 6
        self.params = {"notes": [note.id for note in notes]}

    def to_anki_dict(self):
        return self.__dict__


class AnkiCreateDeckRequest:
    """
        ex:
        {
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": "new deck"
        }
    }
    It is idempotent, so we can just call it without checking if the deck exists
    """

    def __init__(self, deck_name: str):
        self.action = "createDeck"
        self.version = 6
        self.params = {"deck": deck_name}

    def to_anki_dict(self):
        return self.__dict__
