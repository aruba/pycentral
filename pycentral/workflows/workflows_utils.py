import sys, os
import json, yaml

from pycentral.base import ArubaCentralBase

def get_file_contents(filename):
    """Function to open a JSON/YAML file and return the contents of the file in dict format.

    :param filename: Name of an existing JSON/YAML file.
    :type filename: str
    :raises UserWarning: Raises warning when supported filetypes are not provided.
    :return: Data loaded from JSON/YAML file
    :rtype: dict
    """
    input_args = ""
    try:
        with open(filename, "r") as fp:
            file_dummy, file_ext = os.path.splitext(filename)
            if ".json" in file_ext:
                input_args = json.loads(fp.read())
            elif file_ext in ['.yaml', '.yml']:
                input_args = yaml.safe_load(fp.read())
            else:
                raise UserWarning("Provide valid file with"
                                  "format/extension [.json/.yaml/.yml]!")
        return input_args
    except Exception as err:
        print(str(err))
        exit("exiting.. Unable to open file %s!" % filename)

def get_conn_from_file(filename):
    """Creates an instance of class`pycentral.ArubaCentralBase` based on the information
    provided in the YAML/JSON file. \n
        * keyword central_info: A dict containing arguments as accepted by class`pycentral.ArubaCentralBase` \n
        * keyword ssl_verify: A boolean when set to True, the python client validates Aruba Central's SSL certs. \n
        * keyword token_store: Optional. Defaults to None. \n

    :param filename: Name of a JSON/YAML file containing the keywords required for class:`pycentral.ArubaCentralBase` 
    :type filename: str
    :return: An instance of class:`pycentral.ArubaCentralBase` to make API calls and manage access tokens.
    :rtype: class:`pycentral.ArubaCentralBase`
    """
    conn = None
    token_store = None
    ssl_verify = True

    input_args = get_file_contents(filename=filename)
    if "central_info" not in input_args:
        sys.exit("exiting... Provide central_info in the file %s" % filename)
    central_info = input_args["central_info"]

    if "token_store" in input_args:
        token_store = input_args["token_store"]
    if "ssl_verify" in input_args:
        ssl_verify = input_args["ssl_verify"]

    conn = ArubaCentralBase(central_info=central_info, 
                            token_store=token_store, 
                            ssl_verify=ssl_verify)
    return conn