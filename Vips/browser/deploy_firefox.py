import logging
import os.path, os
from sys import platform
from selenium import webdriver
from .selenium_firefox import FirefoxBinary, FirefoxLogInterceptor, Options

DEFAULT_SCREEN_RES = (1366, 768)
logger = logging.getLogger("openwpm")

def get_firefox_binary_path():
    """
    If ../../firefox-bin/firefox-bin or os.environ["FIREFOX_BINARY"] exists,
    return it. Else, throw a RuntimeError.
    """
    if "FIREFOX_BINARY" in os.environ:
        firefox_binary_path = os.environ["FIREFOX_BINARY"]
        if not os.path.isfile(firefox_binary_path):
            raise RuntimeError(
                "No file found at the path specified in "
                "environment variable `FIREFOX_BINARY`."
                "Current `FIREFOX_BINARY`: %s" % firefox_binary_path
            )
        return firefox_binary_path

    root_dir = os.path.dirname(__file__) + "/../.."
    if platform == "darwin":
        firefox_binary_path = os.path.abspath(
            root_dir + "/Nightly.app/Contents/MacOS/firefox-bin"
        )
    else:
        firefox_binary_path = os.path.abspath(root_dir + "/firefox-bin/firefox-bin")

    if not os.path.isfile(firefox_binary_path):
        raise RuntimeError(
            "The `firefox-bin/firefox-bin` binary is not found in the root "
            "of the  OpenWPM directory (did you run the install script "
            "(`install.sh`)?). Alternatively, you can specify a binary "
            "location using the OS environment variable FIREFOX_BINARY."
        )
    return firefox_binary_path

def deploy_firefox() -> webdriver.Firefox:
    """
    launches a firefox instance with parameters set by the input dictionary
    """
    firefox_binary_path = get_firefox_binary_path()

    root_dir = os.path.dirname(__file__)  # directory of this file

    # Use Options instead of FirefoxProfile to set preferences since the
    # Options method has no "frozen"/restricted options.
    # https://github.com/SeleniumHQ/selenium/issues/2106#issuecomment-320238039
    fo = Options()
    # Set a custom profile that is used in-place and is not deleted by geckodriver.
    # https://firefox-source-docs.mozilla.org/testing/geckodriver/CrashReports.html
    # Using FirefoxProfile breaks stateful crawling:
    # https://github.com/mozilla/OpenWPM/issues/423#issuecomment-521018093
    fo.add_argument('--disable-gpu')
    fo.headless = True
    fo.add_argument("--width={}".format(DEFAULT_SCREEN_RES[0]))
    fo.add_argument("--height={}".format(DEFAULT_SCREEN_RES[1]))

    fb = FirefoxBinary(firefox_path=firefox_binary_path)
    driver = webdriver.Firefox(
        firefox_binary=fb,
        options=fo
    )

    # set window size
    driver.set_window_size(*DEFAULT_SCREEN_RES)

    return driver
