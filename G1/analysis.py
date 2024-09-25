"""
File location: ...G1/analysis.py
Description: This file contains the analysis functions for the G1 experiment.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Global imports
from main.constants import R
from main import ureg, Q_
import inspect
from typing import List, Optional

# Third-party imports
import numpy as np
from scipy.stats import linregress
from uncertainties import ufloat
import pandas as pd
import json

# ------------------------------------------
# Analysis functions for G1 experiment
# ------------------------------------------


def lin_func(x: float, m: float) -> float:
    """
    Linear function to calculate y = m * x.
    """

    return m * x


def calc_init_slope(
    x: np.ndarray, y: np.ndarray, min_points: int, threshold: float = 0.99
) -> float:
    """
    Calculate the initial slope of the curve from x and y data.

    Parameters:
    x (np.ndarray): The x data.
    y (np.ndarray): The y data.

    Returns:
    slope (float): The initial slope of the curve.
    """

    from scipy.optimize import curve_fit

    # Initialize the slope and slope error
    slope, r_squared, num_points = None, None, None
    # Fit the linear function to the data and get the slope
    # Calculate slope until the R^2 value is greater than 0.99
    try:
        for i in range(min_points, len(x) + 1):
            popt, pcov = curve_fit(lin_func, x[:i], y[:i])
            # Calculate R^2 value
            y_pred = lin_func(x[:i], *popt)
            ss_res = np.sum((y[:i] - y_pred) * (y[:i] - y_pred))
            ss_tot = np.sum((y[:i] - np.mean(y[:i])) * (y[:i] - np.mean(y[:i])))
            r_sq = 1 - (ss_res / ss_tot)
            # Check if R^2 value is greater than the threshold
            if r_sq >= threshold or i == min_points:
                slope = popt[0]
                slope_err = np.sqrt(np.diag(pcov))[0]
                num_points = i
                r_squared = r_sq
            else:
                break
        if slope is not None:
            slope = ufloat(slope, slope_err)
    except Exception as e:
        # log the error in the console
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")

    return slope, r_squared, num_points


def calc_proc_data(raw_data: dict, file: str) -> dict:
    """
    Calculate the processed data from the raw data.

    Parameters:
    raw_data (dict): A dictionary containing the raw data.
    file (str): The path to the data file.

    Returns:
    proc_data (dict): A dictionary containing the processed data.
    """

    # Extract the required data from the raw data
    data_dict = {
        "id": raw_data["id"],
    }
    for k, v in raw_data.items():
        if k != "id":
            data_dict[k] = v

    # Read the excel file to a pandas dataframe
    df = pd.read_excel(file, engine="openpyxl", header=1)
    # Extract the time and conductivity data
    t = np.array(df["Time [s]"].tolist())
    sigma = np.array(df["Conductivity [μS/cm]"].tolist())
    # Calculate conversion (Xt)
    sigma0 = sigma.max()
    sigma100 = sigma.min()
    Xt = sigma / (sigma100 - sigma0) - sigma0 / (sigma100 - sigma0)
    # Get the index corrsponding to 20% conversion
    idx = np.where(Xt >= 0.25)[0][0]
    # Calculate the initial slope
    slope, r_squared, i = calc_init_slope(x=t, y=Xt, min_points=idx, threshold=0.99)
    # Calculate the rate from the slope and convert to base units
    C_base = Q_(data_dict.get("C_base")).magnitude
    rate = slope * C_base
    rate = rate * ureg("mol / m^3 / s")
    # Append the rate to the data dictionarys
    data_dict["rate"] = f"{rate:.5ue~}"
    data_dict["r_squared"] = r_squared
    Ct = (1 - Xt) * C_base
    # Calculate the dataplot
    plotdata = {
        "x": t.tolist(),
        "y": Ct.tolist(),
        "mode": "markers",
        "type": "scatter",
        "name": "Data",
    }

    # Calculate the fit data plot
    t_fit = t[:i]
    Ct_fit = -rate.nominal_value * t_fit + Ct[0]
    fitdata = {
        "x": t_fit.tolist(),
        "y": Ct_fit.tolist(),
        "mode": "lines",
        "type": "scatter",
        "name": "Fit",
    }

    # Append the plot data to the data dictionary
    data_dict["plotdata"] = plotdata
    data_dict["fitdata"] = fitdata

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


def perform_ea_analysis(ea_dict: dict) -> None:
    """
    Calculate the activation energy (Ea) and plot data from the new or updated
    data in ea_dict.

    Parameters:
    ea_dict (dict): An ea_dict from the G1Results instance containing
    the rate and temperature data.

    Returns:
    None
    """

    # Extract the rate and temperature from the ea_dict and convert to a
    # list of magnitudes. The rate is ufloat with error so we extract the
    # nominal value.
    rate = ea_dict.get("rate")
    T_reaction = ea_dict.get("T_reaction")
    ln_r = [np.log(Q_(x).magnitude.nominal_value) for x in rate]
    T_inv = [1 / Q_(x).magnitude for x in T_reaction]
    unique_T = len(set(T_reaction))

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


def perform_ro_base_analysis(ro_base_dict: dict) -> None:
    """
    Calculate the reaction order using the new or updated data in ro_base_dict
    and also calculate the plot data and add to the dictionary.

    Parameters:
    ro_base_dict (dict): A dictionary containing the reaction order data.

    Returns:
    None
    """

    # Extract the rate and pressure data from the ro_dict and convert to a
    # list of magnitudes. The rate is ufloat with error so we extract the
    # nominal value.
    rate = ro_base_dict.get("rate")
    C_base = ro_base_dict.get("C_base")
    log_r = [np.log10(Q_(x).magnitude.nominal_value) for x in rate]
    # The pressure is in Pa, so divide by 1 bar to get log(p/p0)
    log_C = [np.log10(Q_(x).magnitude / 1.0e5) for x in C_base]
    unique_C = len(set(C_base))

    try:
        # Calculate the reaction order from the rate and pressure data
        slope, intercept, r_squared = calc_slope(log_C, log_r)
        ro_base = slope * ureg("dimensionless")
        # Add the reaction order to the dictionary
        ro_base_dict["ro_base"] = f"{ro_base:.5ue~}"
        ro_base_dict["r_squared"] = r_squared

        # Create the plot data
        plotdata = {
            "x": log_C,
            "y": log_r,
            "mode": "markers",
            "type": "scatter",
            "name": "Data",
        }

        # Create the fitted data curve for the plot
        log_C_fit = np.linspace(
            start=min(log_C) - (max(log_C) - min(log_C)) * 0.1,
            stop=max(log_C) + (max(log_C) - min(log_C)) * 0.1,
            num=100,
        )
        log_r_fit = slope.nominal_value * log_C_fit + intercept.nominal_value
        fitdata = {
            "x": log_C_fit.tolist(),
            "y": log_r_fit.tolist(),
            "mode": "lines",
            "type": "scatter",
            "name": "Fit",
        }

        # Add the plot data and the fit data to the rate dictionary
        ro_base_dict["plotdata"] = plotdata
        ro_base_dict["fitdata"] = fitdata

        # Add error message if unique_p values are less than 3
        if unique_C == 1:
            ro_base_dict["error"] = (
                f"Only one unique pressure value. Need at least three to calculate reaction order. "
                f"Reaction order cannot be calculated. "
                f"Please add more data points to calculate the reaction order."
            )
        elif unique_C == 2:
            ro_base_dict["error"] = (
                f"Only two unique pressure values. Need at least three to calculate reaction order. "
                f"The calculated reaction order is only an estimate. "
                f"Please add more data points at unique pressure to calculate the reaction order accurately."
            )
        elif unique_C >= 3:
            ro_base_dict["error"] = None

    except Exception as e:
        # Log the error message
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")


def perform_ro_ester_analysis(ro_ester_dict: dict) -> None:
    """
    Calculate the reaction order using the new or updated data in ro_base_dict
    and also calculate the plot data and add to the dictionary.

    Parameters:
    ro_ester_dict (dict): A dictionary containing the reaction order data.

    Returns:
    None
    """

    # Extract the rate and pressure data from the ro_dict and convert to a
    # list of magnitudes. The rate is ufloat with error so we extract the
    # nominal value.
    rate = ro_ester_dict.get("rate")
    C_ester = ro_ester_dict.get("C_ester")
    log_r = [np.log10(Q_(x).magnitude.nominal_value) for x in rate]
    # The pressure is in Pa, so divide by 1 bar to get log(p/p0)
    log_C = [np.log10(Q_(x).magnitude / 1.0e5) for x in C_ester]
    unique_C = len(set(C_ester))

    try:
        # Calculate the reaction order from the rate and pressure data
        slope, intercept, r_squared = calc_slope(log_C, log_r)
        ro_ester = slope * ureg("dimensionless")
        # Add the reaction order to the dictionary
        ro_ester_dict["ro_ester"] = f"{ro_ester:.5ue~}"
        ro_ester_dict["r_squared"] = r_squared

        # Create the plot data
        plotdata = {
            "x": log_C,
            "y": log_r,
            "mode": "markers",
            "type": "scatter",
            "name": "Data",
        }

        # Create the fitted data curve for the plot
        log_C_fit = np.linspace(
            start=min(log_C) - (max(log_C) - min(log_C)) * 0.1,
            stop=max(log_C) + (max(log_C) - min(log_C)) * 0.1,
            num=100,
        )
        log_r_fit = slope.nominal_value * log_C_fit + intercept.nominal_value
        fitdata = {
            "x": log_C_fit.tolist(),
            "y": log_r_fit.tolist(),
            "mode": "lines",
            "type": "scatter",
            "name": "Fit",
        }

        # Add the plot data and the fit data to the rate dictionary
        ro_ester_dict["plotdata"] = plotdata
        ro_ester_dict["fitdata"] = fitdata

        # Add error message if unique_p values are less than 3
        if unique_C == 1:
            ro_ester_dict["error"] = (
                f"Only one unique pressure value. Need at least three to calculate reaction order. "
                f"Reaction order cannot be calculated. "
                f"Please add more data points to calculate the reaction order."
            )
        elif unique_C == 2:
            ro_ester_dict["error"] = (
                f"Only two unique pressure values. Need at least three to calculate reaction order. "
                f"The calculated reaction order is only an estimate. "
                f"Please add more data points at unique pressure to calculate the reaction order accurately."
            )
        elif unique_C >= 3:
            ro_ester_dict["error"] = None

    except Exception as e:
        # Log the error message
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")
