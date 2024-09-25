"""
File location; .../G3/simulations.py
Description: This file contains the functions related to simualtions
            for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Global imports
from main import ureg, Q_
from uncertainties import ufloat
from typing import Optional
from main.constants import R
import inspect

# Application imports (if any)
from main.models import Experiment, UserExperiment
from G3.analysis import (
    calc_p_sat,
    calc_tau,
)

# Third-party imports (if any)
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import random

matplotlib.use("Agg")

# ------------------------------------------
# Functions related to defining the simulation parameters
# ------------------------------------------


def p_to_A_func(p: float, p_to_A_factor: float) -> float:
    """
    A Function to calculate the peak area from the pressure value using the
    p_to_A factor.

    Parameters:
    p (float): Pressure in Pa.
    p_to_A_factor (float): p_to_A factor in 1 / Pa.

    Returns:
    A_reactant (float): Reactant peak area in bypass mode (dimensionless).
    """

    return p * p_to_A_factor


def calc_p_to_A_factor(p: list[float], A_reactant: list[float]) -> Optional[tuple]:
    """
    Method to calculate the p_to_A_factor from a list of pressure and
    A_reactant data. The function fits the p_to_A_func to the data and
    returns the p_to_A_factor with error.

    Parameters:
    p (list of floats): List of pressure in Pa.
    A_reactant (list of floats): List of reactant peak areas in bypass mode.

    Returns:
    p_to_A_factor (float): p_to_A factor in 1 / Pa.
    r_squared (float or None): R-squared value of the fit
    """

    from scipy.optimize import curve_fit

    # Create numpy arrays from the lists
    p = np.array(p)
    A_reactant = np.array(A_reactant)

    try:
        # Perform a linear regression to get the slope and intercept
        popt, pcov = curve_fit(p_to_A_func, p, A_reactant, maxfev=10000)
        # Get the values and errors
        p_to_A_val = popt[0]
        std_err = np.sqrt(np.diag(pcov))
        p_to_A_err = std_err[0]
        # Convert the values to uncertainties
        p_to_A_factor = ufloat(p_to_A_val, p_to_A_err)
        # Calculate the R-squared value
        residuals = A_reactant - p_to_A_func(p, p_to_A_val)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((A_reactant - np.mean(A_reactant)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        return p_to_A_factor, r_squared
    except Exception as e:
        # Log the error in console and return None
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")

        return None, None


def calc_kinetic_params(
    instance: object,
    tau: list[float],
    p: list[float],
    T_reactor: list[float],
    conversion: list[float],
) -> Optional[tuple]:
    """
    Estimate the kinetic parameters for the G3 experiment.

    Parameters:
    tau (list of floats): List of residence times in kg * s / mol.
    p (list of floats): List of pressure values in Pa.
    T_reactor (list of floats): List of reactor temperatures in K.
    conversion (list of floats): List of conversion values.

    Returns:
    A_app (float): Pre-exponential factor in the Arrhenius equation.
    Ea (float): Activation energy
    ro (float): Reaction order
    """

    from scipy.optimize import curve_fit
    from G3.models import G3Results

    # Create numpy arrays from the lists
    tau = np.array(tau)
    p = np.array(p)
    T_reactor = np.array(T_reactor)
    conversion = np.array(conversion)

    # Initialize the guess values from Global Simulation Parameters
    initial_guess = [29.453551, 132648, 1.0]
    # Calculate the kinetic parameters using curve fitting
    try:
        x_data = np.vstack((tau, p, T_reactor))
        y_data = conversion
        popt, pcov = curve_fit(kin_func, x_data, y_data, maxfev=10000, p0=initial_guess)
        # Get the values and errors
        A_app_val, Ea_val, ro_val = popt
        std_err = np.sqrt(np.diag(pcov))
        A_app_err, Ea_err, ro_err = std_err
        # Convert the values to uncertainties
        A_app = ufloat(A_app_val, A_app_err)
        Ea = ufloat(Ea_val, Ea_err)
        ro = ufloat(ro_val, ro_err)
        # Get the r_squared value
        residuals = y_data - kin_func(x_data, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

    except Exception as e:
        # If the calculation fails, log the error and return None
        print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")

        return None, None, None, None

    return A_app, Ea, ro, r_squared


def kin_func(X: tuple, A_app: float, Ea: float, ro: float) -> float:
    """
    Function to calculate the conversion in a plug flow reactor for a given set
    values of the kinetic parameters.

    Parameters:
    X (tuple): Tuple containing the values of (tau, p, and T_reactor)
    A_app (float): Pre-exponential factor in the Arrhenius equation. It is
    in the exponential form.
    Ea (float): Activation energy in J/mol.
    ro (float): Reaction order in the reactant.

    Returns:
    convrsion (float): Conversion in the reactor.
    """

    # Extract the values from the tuple
    tau, p, T_reactor = X
    # number of slices in the reactor the numerical integration
    n_slices = 100
    conversions = []

    for st, p0, t_r in zip(tau, p, T_reactor):
        k = np.exp(A_app - (Ea / (R.magnitude * t_r)))
        tau_slice = st / n_slices
        # Integrate the kinetic equation over the slices
        p_in = p0

        for i in range(n_slices):
            r = k * (p_in / 1.0e5) ** ro
            X_slice = r * tau_slice
            p_out = max((1 - X_slice) * p_in, 0)
            p_in = p_out

        conversion = (p0 - p_out) / p0
        conversions.append(conversion)

    return np.array(conversions)


# ------------------------------------------
# Functions related to performing the simulation
# ------------------------------------------


def perform_simulation(userexperiment, input_data):
    """
    This function performs the simulations for the G3 experiment.

    Parameters:
    userexperiment (object): UserExperiment instance.
    input_data (dict): Dictionary containing the input data for the simulation.

    Returns:
    output_data (dict): Dictionary containing the output data from the simulation.
    """

    # Get the input data from the user form
    M_catalyst = Q_(input_data.get("M_catalyst")).to_base_units()
    V_flow = Q_(input_data.get("V_flow")).to_base_units()
    T_reactor = Q_(input_data.get("T_reactor")).to_base_units()
    T_bath = Q_(input_data.get("T_bath")).to_base_units()
    # Convert the quantities to magnitudes for calculation
    M_catalyst = M_catalyst.magnitude
    V_flow = V_flow.magnitude
    T_reactor = T_reactor.magnitude
    T_bath = T_bath.magnitude
    # Calculate the saturation pressure and residence time
    p_sat = calc_p_sat(T_bath=T_bath, Substance="Ethanol")
    tau = calc_tau(M_catalyst=M_catalyst, V_flow=V_flow, p=p_sat, T_bath=T_bath)

    # Get the simulation parameters, if available
    from G3.models import G3SimulParams, G3SimulGlobalParams

    g3params = G3SimulParams.objects.get(userexperiment=userexperiment)
    g3globalparams = G3SimulGlobalParams.objects.first()
    simul_params = g3params.simul_params
    global_params = g3globalparams.params

    p_to_A_params = global_params.get("p_to_A_params")
    p_to_A_factor = Q_(p_to_A_params.get("p_to_A_factor")).magnitude
    # Check if the p_to_A_params are available for the userexperiment
    if simul_params.get("p_to_A_params"):
        r_squared = float(simul_params.get("p_to_A_params").get("r_squared"))
        if r_squared >= 0.995:
            p_to_A_params = simul_params.get("p_to_A_params")
            p_to_A_factor = Q_(
                p_to_A_params.get("p_to_A_factor")
            ).magnitude.nominal_value

    # Calculate the reactant peak area from the pressure and p_to_A factor
    A_reactant = p_to_A_func(p_sat, p_to_A_factor)

    kinetic_params = global_params.get("kinetic_params")
    Ea = Q_(kinetic_params.get("Ea")).magnitude
    A_app = Q_(kinetic_params.get("A_app")).magnitude
    ro = Q_(kinetic_params.get("ro")).magnitude

    # Check if the kinetic_params are available for the userexperiment
    if simul_params.get("kinetic_params"):
        r_squared = float(simul_params.get("kinetic_params").get("r_squared"))
        if r_squared >= 0.995:
            kinetic_params = simul_params.get("kinetic_params")
            Ea = float(Q_(kinetic_params.get("Ea")).magnitude.nominal_value)
            A_app = float(Q_(kinetic_params.get("A_app")).magnitude.nominal_value)
            ro = float(Q_(kinetic_params.get("ro")).magnitude.nominal_value)
    kinetic_params = [A_app, Ea, ro]

    # Perform the simulation
    input_data = ([tau], [p_sat], [T_reactor])
    conversion = kin_func(input_data, *kinetic_params)
    noise = random.gauss(0.0, 2.5)
    A_product = conversion[0] * (1 + noise / 100) * A_reactant

    # Save the results to the output variable
    output_data = {
        "A_reactant": f"{A_reactant:.1f}",
        "A_product": f"{A_product:.1f}",
    }

    return output_data
