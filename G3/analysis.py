"""
File location; .../G3/analysis.py
Description: This file contains the analysis functions for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Global imports
from main import ureg, Q_
from typing import List, Optional
import inspect
from . import logger

# Application imports
from main.constants import R
from G3.constants import AntoineConstants

# Third-party imports
from scipy.stats import linregress
import numpy as np
from uncertainties import ufloat

# ------------------------------------------
# Data analysis functions and methods
# ------------------------------------------


def calc_p_sat(T_bath: float, Substance: str = "Ethanol") -> Optional[float]:
    """
    Calculate the saturation pressure from Antoine equation.
    NOTE: All calculations are performed in base units.

    Parameters:
    T_bath (float): Temperature of the water bath in K
    Substance (str): The substance for which the saturation pressure
    is to be calculated. Default is "Ethanol".

    Returns:
    p_sat (float or None): The saturation pressure in Pa.
    """

    # Get the Antoine constants for the substance
    A = Q_(AntoineConstants[Substance]["A"]).magnitude
    B = Q_(AntoineConstants[Substance]["B"]).magnitude
    C = Q_(AntoineConstants[Substance]["C"]).magnitude

    # Calculate the saturation pressure using Antoine equation ->
    # log10(p_sat) = A - B / (T + C)
    try:
        p_sat = 10 ** (A - B / (T_bath + C))
        # Antoine equation returns pressure in bar, convert to Pa.
        p_sat = p_sat * 1.0e5
    except:
        # If the calculation fails return None.
        return None

    return p_sat


def calc_tau(
    M_catalyst: float, V_flow: float, p: float, T_bath: float
) -> Optional[float]:
    """
    Calculate the space time from the given parameters.
    NOTE: All calculations are performed in base units.

    Parameters:
    M_catalyst (float): Mass of the catalyst in kg.
    V_flow (float): Flow rate in mol / s.
    p (float): Partial pressure of reactant in Pa
    T_bath (float): Water bath temperature in K.

    Returns:
    tau (float or None): The space time in kg * s / mol.
    """

    try:
        # Calculate concentration from ideal gas law -> C = P / (R * T)
        C_substance = p / (R.magnitude * T_bath)
        # Molar flow rate -> n = C * V
        n_substance = C_substance * V_flow
        # Space time -> tau = M / n
        tau = M_catalyst / n_substance
    except:
        # If the calculation fails, return None.
        tau = None

    return tau


def calc_conv(A_reactant: float, A_product: float) -> Optional[float]:
    """
    Calculate the conversion from the given peak areas of reactant in
    bypass mode and product in reactor mode.

    Parameters:
    A_reactant (float): Peak area of reactant in bypass mode.
    A_product (float): Peak area of product in reactor mode.

    Returns:
    conversion (float or None): Conversion of the reactant as a fraction.
    """

    try:
        # Calculate the conversion from the peak areas.
        # If conversion is more than one, set it to one.
        conversion = min(A_product / A_reactant, 1.0)
    except Exception as e:
        # If the calculation fails, log the error and return None.
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")
        conversion = None

    return conversion


def calc_proc_data(raw_data: dict) -> dict:
    """
    Calculate the space time, saturation pressure and conversion
    from the given raw data for a G3Data instance.

    Parameters:
    raw_data (dict): A dictionary containing the raw data.

    Returns:
    proc_data (dict): A dictionary containing the processed data.
    """

    # Extract data from the raw data dictionary
    id = raw_data["id"]
    mag = {}
    for k, v in raw_data.items():
        if k != "id":
            if isinstance(v, str):
                mag[k] = Q_(v).magnitude if raw_data.get(k) else None
            elif isinstance(v, bool):
                mag[k] = v

    # Calculate p_reac, tau and conversion
    p = calc_p_sat(mag["T_bath"], Substance="Ethanol")
    tau = calc_tau(
        M_catalyst=mag["M_catalyst"],
        V_flow=mag["V_flow"],
        p=p,
        T_bath=mag["T_bath"],
    )
    conversion = calc_conv(mag["A_reactant"], mag["A_product"])

    # Convert all values to base units
    p = p * ureg.Pa if p is not None else None
    tau = tau * ureg.kg * ureg.s / ureg.mol if tau is not None else None
    conversion = Q_(conversion) if conversion is not None else None
    T_reactor = mag["T_reactor"] * ureg.kelvin

    # Create a dictionary to store the calculated values.
    data_dict = {
        "id": id,
        "tau": f"{tau:~}" if tau is not None else None,
        "p": f"{p:~}" if p is not None else None,
        "conversion": f"{conversion:~}" if conversion is not None else None,
        "T_reactor": f"{T_reactor:~}" if T_reactor is not None else None,
        "is_active": raw_data.get("is_active"),
        "is_simulated": raw_data.get("is_simulated"),
    }

    return data_dict


def calc_slope(x: List[float], y: List[float]) -> Optional[float]:
    """
    A general function to calculate the slope with error and intercept
    with error from the given x and y values.
    NOTE: x and y are list of floats or magnitudes. Do not pass ureg quantities.

    Parameters:
    x (List[float]): The x values for the curve.
    y (List[float]): The y values for the curve.

    Returns:
    slope (ufloat): The slope of the curve with error.
    intercept (ufloat): The intercept of the curve with error.
    r_squared (float): The R-squared value of fitting.
    """

    # Create numpy arrays with just magnitudes
    x_arr = np.array(x)
    y_arr = np.array(y)

    try:
        # Use linear regression to calculate the slope of the curve
        results = linregress(x_arr, y_arr)
        slope = ufloat(results.slope, results.stderr)
        intercept = ufloat(results.intercept, results.intercept_stderr)
        r_squared = results.rvalue**2
    except Exception as e:
        # log the error message in console
        print(f"Error in {__name__}: {e}")
        # If the calculation fails, return None
        return None

    return (slope, intercept, r_squared)


def tau_conv_func(tau: float, rate: float) -> Optional[float]:
    """
    Calculate the conversion from the given tau and rate data.

    Parameters:
    tau (float): The space time data in kg * s / mol.
    rate (float): The rate of the reaction in mol / (kg * s).

    Returns:
    conversion (float or None): The conversion of the reactant.
    """

    # Calculate the conversion from the given tau and rate data
    conversion = tau * rate

    return conversion


def calc_rate(tau: List[float], conversion: List[float]) -> Optional[float]:
    """
    Calculate the rate from the given tau and conversion data.
    NOTE: tau and conversion are list of floats or magnitudes. Do not pass
    ureg quantities.

    Parameters:
    tau (List[float]): The space time data in kg * s / mol.
    conversion (List[float]): The conversion as a fraction.

    Returns:
    rate with error (float): The rate of the reaction in mol / (kg * s).
    r_squared (float): The R-squared value of fitting.
    """

    from scipy.optimize import curve_fit

    # Create numpy arrays with just magnitudes
    tau_arr = np.array(tau)
    conversion_arr = np.array(conversion)

    try:
        # Use scipy curve_fit to calculate the rate of the reaction
        popt, pcov = curve_fit(tau_conv_func, tau_arr, conversion_arr)
        rate_val = popt
        rate_err = np.sqrt(np.diag(pcov))
        rate = ufloat(rate_val, rate_err)
        # calculate r-squared value
        residuals = conversion_arr - tau_conv_func(tau_arr, rate_val)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((conversion_arr - np.mean(conversion_arr)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

    except Exception as e:
        # log the error message in console
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")
        # If the calculation fails, return None
        return None

    return (rate, r_squared)


def perform_rate_analysis(rate_dict: dict) -> None:
    """
    Process the rate data in rate_dict and update with plot data and
    calculated rate.

    Parameters:
    rate_dict (dict): A dictionary containing the data for rate analysis.

    Returns:
    None
    """

    # Extract the tau and conversion data from the dictionary and convert
    # to a list of magnitudes
    tau = rate_dict.get("tau")
    conversion = rate_dict.get("conversion")
    is_simulated = rate_dict.get("is_simulated")
    tau = [Q_(x).magnitude for x in tau]
    conversion = [Q_(x).magnitude for x in conversion]
    is_simulated = [x for x in is_simulated]
    unique_tau = len(set(tau))

    # Add zero point to the tau and conversion data
    tau.append(0.0)
    conversion.append(0.0)
    is_simulated.append(False)

    try:
        # Calculate the rate based on tau and conversion data and add to dictionary
        rate, r_squared = calc_rate(tau, conversion)
        rate = rate * ureg("mol/(kg*s)") if rate else None
        rate_dict["rate"] = f"{rate:.5ue~}" if rate else None
        rate_dict["r_squared"] = r_squared if r_squared else None

        # Create the fit data for plotting
        tau_fit = np.linspace(
            start=min(tau) - (max(tau) - min(tau)) * 0.1,
            stop=max(tau) + (max(tau) - min(tau)) * 0.1,
            num=100,
        )
        conversion_fit = rate.nominal_value * tau_fit

        # Remove simulated data from tau and add to another list
        tau_simul = []
        conversion_simul = []
        tau_exp = []
        conversion_exp = []

        for i in range(len(is_simulated)):
            if is_simulated[i] == True:
                tau_simul.append(tau[i])
                conversion_simul.append(conversion[i])
            elif is_simulated[i] == False:
                tau_exp.append(tau[i])
                conversion_exp.append(conversion[i])

        # Create the tau vs conversion plot data for experimental data
        plotdata = {
            "x": tau_exp,
            "y": conversion_exp,
            "mode": "markers",
            "type": "scatter",
            "name": "Exp",
        }

        simuldata = {
            "x": tau_simul,
            "y": conversion_simul,
            "mode": "markers",
            "type": "scatter",
            "name": "Sim",
        }

        fitdata = {
            "x": tau_fit.tolist(),
            "y": conversion_fit.tolist(),
            "mode": "lines",
            "type": "scatter",
            "name": "Fit",
        }

        # Add the plot data and the fit data to the rate dictionary
        rate_dict["plotdata"] = plotdata
        rate_dict["fitdata"] = fitdata
        rate_dict["simuldata"] = simuldata

        # Add error message if unique tau values are less than 3
        if unique_tau == 1:
            rate_dict["error"] = (
                f"Only one unique tau value. Need at least three to calculate rate. "
                f"The calculated rate is only an estimate and will not be used for further calculations. "
                f"Please add more data points to calculate the rate accurately."
            )
        elif unique_tau == 2:
            rate_dict["error"] = (
                f"Only two unique tau values. Need at least three to calculate rate. "
                f"The calculated rate is only an estimate and will not be used for further calculations. "
                f"Please add more data points to calculate the rate accurately."
            )
        elif unique_tau >= 3:
            rate_dict["error"] = None

    except Exception as e:
        # Log the error message in console
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")


def perform_ea_analysis(ea_dict: dict) -> None:
    """
    Calculate the activation energy (Ea) and plot data from the new or updated
    data in ea_dict.

    Parameters:
    ea_dict (dict): An ea_dict from the G3Results instance containing
    the rate and temperature data.

    Returns:
    None
    """

    # Extract the rate and temperature from the ea_dict and convert to a
    # list of magnitudes. The rate is ufloat with error so we extract the
    # nominal value.
    rate = ea_dict.get("rate")
    T_reactor = ea_dict.get("T_reactor")
    ln_r = [np.log(Q_(x).magnitude.nominal_value) for x in rate]
    T_inv = [1 / Q_(x).magnitude for x in T_reactor]
    unique_T = len(set(T_reactor))

    try:
        # Calculate the activation energy and pre-exponential factor
        slope, intercept, r_squared = calc_slope(T_inv, ln_r)
        Ea = -slope * R.magnitude * ureg("J/mol")
        A_app = intercept * ureg("dimensionless")
        # Add the Ea and A_app to the dictionary
        ea_dict["Ea"] = f"{Ea:.5ue~}"
        ea_dict["A_app"] = f"{A_app:.5ue~}"
        ea_dict["r_squared"] = r_squared

        # Create the plot data
        plotdata = {
            "x": T_inv,
            "y": ln_r,
            "mode": "markers",
            "type": "scatter",
            "name": "Data",
        }

        # Create the fit data plot
        T_inv_fit = np.linspace(
            start=min(T_inv) - (max(T_inv) - min(T_inv)) * 0.1,
            stop=max(T_inv) + (max(T_inv) - min(T_inv)) * 0.1,
            num=100,
        )
        ln_r_fit = slope.nominal_value * T_inv_fit + intercept.nominal_value
        fitdata = {
            "x": T_inv_fit.tolist(),
            "y": ln_r_fit.tolist(),
            "mode": "lines",
            "type": "scatter",
            "name": "Fit",
        }

        # Add the plot data and the fit data to the rate dictionary
        ea_dict["plotdata"] = plotdata
        ea_dict["fitdata"] = fitdata

        # Add error message if unique_T values are less than 3
        if unique_T == 1:
            ea_dict["error"] = (
                f"Only one unique T_reactor value. Need at least three to calculate Ea. "
                f"Activation energy cannot be calculated. "
                f"Please add more data points to calculate the Ea."
            )
        elif unique_T == 2:
            ea_dict["error"] = (
                f"Only two unique T_reactor values. Need at least three to calculate Ea. "
                f"The calculated Ea is only an estimate. "
                f"Please add more data points at different T to calculate the Ea accurately."
            )
        elif unique_T >= 3:
            ea_dict["error"] = None

    except Exception as e:
        # Log the error message
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")


def perform_ro_analysis(ro_dict: dict) -> None:
    """
    Calculate the reaction order using the new or updated data in ro_dict
    and also calculate the plot data and add to the dictionary.

    Parameters:
    ro_dict (dict): A dictionary containing the reaction order data.

    Returns:
    None
    """

    # Extract the rate and pressure data from the ro_dict and convert to a
    # list of magnitudes. The rate is ufloat with error so we extract the
    # nominal value.
    rate = ro_dict.get("rate")
    p = ro_dict.get("p")
    log_r = [np.log10(Q_(x).magnitude.nominal_value) for x in rate]
    # The pressure is in Pa, so divide by 1 bar to get log(p/p0)
    log_p = [np.log10(Q_(x).magnitude / 1.0e5) for x in p]
    unique_p = len(set(p))

    try:
        # Calculate the reaction order from the rate and pressure data
        slope, intercept, r_squared = calc_slope(log_p, log_r)
        r_order = slope * ureg("dimensionless")
        # Add the reaction order to the dictionary
        ro_dict["r_order"] = f"{r_order:.5ue~}"
        ro_dict["r_squared"] = r_squared

        # Create the plot data
        plotdata = {
            "x": log_p,
            "y": log_r,
            "mode": "markers",
            "type": "scatter",
            "name": "Data",
        }

        # Create the fitted data curve for the plot
        log_p_fit = np.linspace(
            start=min(log_p) - (max(log_p) - min(log_p)) * 0.1,
            stop=max(log_p) + (max(log_p) - min(log_p)) * 0.1,
            num=100,
        )
        log_r_fit = slope.nominal_value * log_p_fit + intercept.nominal_value
        fitdata = {
            "x": log_p_fit.tolist(),
            "y": log_r_fit.tolist(),
            "mode": "lines",
            "type": "scatter",
            "name": "Fit",
        }

        # Add the plot data and the fit data to the rate dictionary
        ro_dict["plotdata"] = plotdata
        ro_dict["fitdata"] = fitdata

        # Add error message if unique_p values are less than 3
        if unique_p == 1:
            ro_dict["error"] = (
                f"Only one unique pressure value. Need at least three to calculate reaction order. "
                f"Reaction order cannot be calculated. "
                f"Please add more data points to calculate the reaction order."
            )
        elif unique_p == 2:
            ro_dict["error"] = (
                f"Only two unique pressure values. Need at least three to calculate reaction order. "
                f"The calculated reaction order is only an estimate. "
                f"Please add more data points at unique pressure to calculate the reaction order accurately."
            )
        elif unique_p >= 3:
            ro_dict["error"] = None

    except Exception as e:
        # Log the error message
        print(f"Error in {__name__}: {e}")
