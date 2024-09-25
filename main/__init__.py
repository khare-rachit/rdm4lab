from pint import UnitRegistry

# Initialize the UnitRegistry
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
Q_ = ureg.Quantity

# Define percent as a unit
ureg.define("percent = 0.01 = %")

# Define arbitrary unit normalized values
ureg.define("unitless = 1 = ul")

# Export these for global usage
__all__ = ["ureg", "Q_"]
