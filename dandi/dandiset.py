"""Classes/utilities for support of a dandiset"""

import yaml
from pathlib import Path

from .consts import dandiset_metadata_file
from .utils import find_parent_directory_containing

from . import get_logger

lgr = get_logger()


class Dandiset(object):
    """A prototype class for all things dandiset
    """

    __slots__ = ["metadata", "path", "path_obj", "_metadata_file_obj"]

    def __init__(self, path, allow_empty=False):
        self.path = str(path)
        self.path_obj = Path(path)
        if not allow_empty and not (self.path_obj / dandiset_metadata_file).exists():
            raise ValueError(f"No dandiset at {path}")

        self.metadata = None
        self._metadata_file_obj = self.path_obj / dandiset_metadata_file
        self._load_metadata()

    @classmethod
    def find(cls, path):
        """Find a dandiset possibly pointing to a directory within it
        """
        dandiset_path = find_parent_directory_containing(dandiset_metadata_file, path)
        if dandiset_path:
            return cls(dandiset_path)
        return None

    def _load_metadata(self):
        if self._metadata_file_obj.exists():
            with open(self._metadata_file_obj) as f:
                # TODO it would cast 000001 if not explicitly string into
                # an int -- we should prevent it... probably with some custom loader
                self.metadata = yaml.safe_load(f)
        else:
            self.metadata = None

    def update_metadata(self, meta):
        """Update existing metadata record in dandiset.yaml
        """
        if not meta:
            lgr.debug("No updates to metadata, returning")
            return

        header = """\
# DO NOT EDIT this file manually.
# It can be obtained from the dandiarchive, and updated using dandi organize
"""

        # We will use ruaml to load/save it
        # Seems to be too tricky to add new entries, etc so we will
        # just resort to explicitly adding the header while saving
        # import ruamel.yaml
        # yaml = ruamel.yaml.YAML()  # defaults to round-trip if no parameters
        # given
        if self._metadata_file_obj.exists():
            with open(self._metadata_file_obj) as f:
                rec = yaml.load(f)
        else:
            rec = {}

        # TODO: decide howto and properly do updates to nested structures if
        # possible.  Otherwise limit to the fields we know could be modified
        # locally
        rec.update(meta)

        with open(self._metadata_file_obj, "w") as f:
            f.write(header)
            yaml.dump(rec, f)

        # and reload now by a pure yaml
        self._load_metadata()

    @property
    def identifier(self):
        return self.metadata["identifier"]
