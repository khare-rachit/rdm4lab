# main/constants.py
# Define all the constants used in the application here.

from main import ureg

R = 8.31446261815324 * ureg.joule / (ureg.kelvin * ureg.mole)

AntoineConstants = {
    "Ethanol": {"A": "5.37229", "B": "1670.409 K", "C": "-40.191 K"},
}
