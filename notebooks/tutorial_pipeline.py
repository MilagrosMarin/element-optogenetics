import os
import pathlib
import datajoint as dj
from element_animal import subject
from element_animal.subject import Subject
from element_lab import lab
from element_lab.lab import Lab, Location, Project, Protocol, Source, User
from element_lab.lab import Device as Equipment
from element_lab.lab import User as Experimenter
from element_session import session_with_datetime as session
from element_session.session_with_datetime import Session
from element_optogenetics import optogenetics


if "custom" not in dj.config:
    dj.config["custom"] = {}

# overwrite dj.config['custom'] values with environment variables if available

dj.config["custom"]["database.prefix"] = os.getenv(
    "DATABASE_PREFIX", dj.config["custom"].get("database.prefix", "")
)

dj.config["custom"]["ephys_root_data_dir"] = os.getenv(
    "EPHYS_ROOT_DATA_DIR", dj.config["custom"].get("ephys_root_data_dir", "")
)

db_prefix = dj.config["custom"].get("database.prefix", "")


# Declare functions for retrieving data
def get_ephys_root_data_dir():
    """Retrieve ephys root data directory."""
    ephys_root_dirs = dj.config.get("custom", {}).get("ephys_root_data_dir", None)
    if not ephys_root_dirs:
        return None
    elif isinstance(ephys_root_dirs, (str, pathlib.Path)):
        return [ephys_root_dirs]
    elif isinstance(ephys_root_dirs, list):
        return ephys_root_dirs
    else:
        raise TypeError("`ephys_root_data_dir` must be a string, pathlib, or list")


# Activate schemas
lab.activate(db_prefix + "lab")
subject.activate(db_prefix + "subject", linking_module=__name__)
session.activate(db_prefix + "session", linking_module=__name__)


@lab.schema
class SkullReference(dj.Lookup):
    definition = """
    skull_reference   : varchar(60)
    """
    contents = zip(["Bregma", "Lambda"])


def get_session_directory(session_key):
    session_directory = (session.SessionDirectory & session_key).fetch1("session_dir")
    return pathlib.Path(session_directory)


optogenetics.activate(db_prefix + "optogenetics", linking_module=__name__)
