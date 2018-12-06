import json
import logging
import signal
import subprocess
from functools import lru_cache
from pprint import pprint
from subprocess import PIPE, CalledProcessError

import semver
from cached_property import cached_property

BRIGHTSIDE_NAME = "Brightside"
log = logging.getLogger(__name__)
_version = None


class BrightCallError(Exception):
    def __init__(self, returncode, cmd, arguments, output=None, stderr=None):
        self.returncode = returncode
        self.cmd = cmd
        self.arguments = arguments
        self.output = self.stdout = output
        self.stderr = stderr
        self.errors = None
        self.message = None

    def __str__(self):
        if self.returncode and self.returncode < 0:
            return "Command '%s' died with %d." % (self.cmd, -self.returncode)
        else:
            if self.stderr:
                return "%s command with arguments '%s' returned non-zero exit status %d and error: %s" % (
                    BRIGHTSIDE_NAME, self.arguments, self.returncode, self.stderr)
            else:
                return "%s command with arguments '%s' returned non-zero exit status %d." % (
                    BRIGHTSIDE_NAME, self.arguments, self.returncode)

    def __repr__(self):
        return "BrightCallError(%s, %s, %s, %s, %s)" % (repr(self.returncode), repr(self.cmd), repr(self.arguments), repr(self.stdout), repr(self.stderr))


@lru_cache(maxsize=None)
def version():
    """
    Returns full version of the CA Brightside that is installed globally as ``bright`` commmand as a string - e.g. ``1.0.2-next.201806261725``.

    The version obtained only once. Subquent calls to this function return the same value.

    You can use ``semver`` module to parse it and compare:

        if not semver.match(version(), ">=1.0.1")):
            ...
    """
    return _version()


def _version():
    data = bright("--version")
    return data["version"].strip()


def _call_command_and_parse_json(command):
    cp = subprocess.run(command, shell=True, stdout=PIPE,
                        stderr=PIPE, encoding="utf8", check=True)
    if cp.stdout:                    
        j = json.loads(cp.stdout)
    else:
        j = None
    log.debug("JSON: j")
    log.debug("command_response: %s " % cp)
    return j, cp


def bright(args, return_data=True):
    """
    Executes CA Brightside with arguments of this function. The response is returned as Python data structures.

    Parameter ``return_data`` is by default ``True`` and it caused to return only the data section without metadata.

    Metadata are processed automatically and if they mean that commands was not successful and ``BrightCallError`` exception
    is raised.

    Example:

        jobs = bright("zos-jobs list jobs")

        # jobs is equal to:
        [{'class': 'A',
        'files-url': 'https://ca32.ca.com:1443/zosmf/restjobs/jobs/J0038667USILCA11D4B949F2.......%3A/files',
        'job-correlator': 'J0038667USILCA11D4B949F2.......:',
        'jobid': 'JOB38667',
        'jobname': 'PLAPALLC',
        'owner': 'PLAPE03',
        'phase': 20,
        'phase-name': 'Job is on the hard copy queue',
        'retcode': 'SEC ERROR',
        'status': 'OUTPUT',
        'subsystem': 'JES2',
        'type': 'JOB',
        'url': 'https://ca32.ca.com:1443/zosmf/restjobs/jobs/J0038667USILCA11D4B949F2.......%3A'}]
    """
    if not isinstance(args, str):
        args = subprocess.list2cmdline(args)

    command = f"bright --rfj {args}"
    try:
        j, cp = _call_command_and_parse_json(command)
        if j is None:
            return None
        if not j.get("success"):
            be = BrightCallError(cp.returncode, command,
                                 args, output=cp.stdout, stderr=cp.stderr)
            be.errors = j.get("errors")
            be.message = j.get("message")
        else:
            if "data" in j and return_data:
                return j["data"]
            return j

    except CalledProcessError as e:
        log.debug("error: %s, output=%s" % (repr(e), e.output))
        if e.stderr:
            raise BrightCallError(e.returncode, e.cmd,
                                  args, output=e.output, stderr=e.stderr)
        else:
            j = json.loads(e.output)
            be = BrightCallError(e.returncode, e.cmd, args, output=j.get(
                "stdout"), stderr=j.get("stderr"))
            be.errors = j.get("errors")
            be.message = j.get("message")
            raise be


def check_brightside_version():
    v = version()
    log.debug("%s version: %s" % (BRIGHTSIDE_NAME, v))
    required_version = ">=1.0.1"
    if not semver.match(v, required_version):
        print("pybright requires %s %s but it is %s" %
              (BRIGHTSIDE_NAME, required_version, v))


check_brightside_version()
