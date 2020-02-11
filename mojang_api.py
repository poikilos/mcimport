#!/usr/bin/env python
import json
python_mr = 3  # major revision
try:
    import urllib.request
    urlopen = urllib.request.urlopen
except ImportError:
    python_mr = 2
    from urllib2 import urlopen
# try:
    # import urllib.request
    # request = urllib.request
# except ImportError:
    # # python2
    # import urllib2 as urllib
    # import urllib2
    # request = urllib

import sys
api_url = "https://api.mojang.com"
def error(msg):
    sys.stderr.write(msg + "\n")

def get_uuid(username):
    """
    Get the most recent name of a player using the Mojang web API.
    """
    name = None
    api_uuid_url_fmt = api_url + "/users/profiles/minecraft/{username}"
    url = api_uuid_url_fmt.format(username=username)
    raise RuntimeError("not yet implemented")


def get_names(uuid):
    """
    Get name objects from the Mojang web API, convert each
    object to a string.

    Returns the list of names.

    Example return of url:
    "[
      {
        "name": "Gold"
      },
      {
        "name": "Diamond",
        "changedToAt": 1414059749000
      }
    ]"

    Example return of function:
    [Gold, Diamond]
    """
    if "-" in uuid:
        # error("WARNING: '-' characters will be removed from UUID.")
        uuid = uuid.replace("-", "")
    names = None
    api_name_url_fmt = api_url + "/user/profiles/{uuid}/names"
    url = api_name_url_fmt.format(uuid=uuid)
    # response = urlopen(url)
    # req = urllib2.Request(url)
    # req = request(url)
    # See <https://stackoverflow.com/questions/43048132/
    # download-text-file-from-url-python>
    response = urlopen(url)
    data = response.read()
    data_s = data.decode()
    if len(data_s) > 0:
        try:
            events = json.loads(data_s)
        except ValueError as e:
            error("ERROR: cannot interpret JSON: '{}'".format(data_s))
            raise e
        for event in events:
            if names is None:
                names = []
            names.append(event["name"])
    else:
        error("WARNING: The UUID is not valid.")
    return names

def get_name(uuid):
    name = None
    names = get_names(uuid)
    if (names is not None) and (len(names) > 0):
        name = names[-1]
    return name

def get_skin_url(uuid):
    """
    Sequential Arguments
    uuid -- crafatar's 3rd-party API allows UUIDs with/without hyphens.
    """
    api_skin_url_fmt = "https://crafatar.com/skins/{uuid}"
    return api_skin_url_fmt.format(uuid=uuid)

def get_cape_url(uuid):
    """
    Sequential Arguments
    uuid -- crafatar's 3rd-party API allows UUIDs with/without hyphens.

    Return the URL.
    NOTE: The URL returns 0 bytes usually. Only certain people have
    capes, such as if they won a contest, participated in an event, or
    work for Mojang.
    """
    api_cape_url_fmt = "https://crafatar.com/capes/{uuid}"
    return api_skin_url_fmt.format(uuid=uuid)

def get_face_url(uuid):
    """
    Sequential Arguments
    uuid -- crafatar's 3rd-party API allows UUIDs with/without hyphens.
    """
    api_face_url_fmt = "https://crafatar.com/avatars/{uuid}"
    return api_face_url_fmt.format(uuid=uuid)

def main():
    # testAbiyahhUUID = "5f7f4afe-a5d5-46b8-84f6-89ebe74bd4a5"
    # test_name = get_name(testAbiyahhUUID)
    # if test_name is not None:
    #     error("SUCCESSFULLY GOT USERNAME: " + test_name)
    # else:
    #     error("FAILED TO GET USERNAME")
    # error("")
    if len(sys.argv) < 2:
        error("You must specify a UUID")
        exit(1)
    uuid = sys.argv[1].replace("-", "")
    name = get_name(uuid)
    if name is not None:
        print(name)
    else:
        print("<unknown>")

if __name__ == "__main__":
    main()
