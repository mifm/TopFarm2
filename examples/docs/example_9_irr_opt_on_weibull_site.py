import numpy as np
from openmdao.api import view_model
from py_wake.examples.data.iea37._iea37 import IEA37_WindTurbines, IEA37Site
from py_wake.wake_models.gaussian import IEA37SimpleBastankhahGaussian
from py_wake.aep_calculator import AEPCalculator
from topfarm.cost_models.economic_models.turbine_cost import economic_evaluation
from topfarm.cost_models.cost_model_wrappers import CostModelComponent
from topfarm import TopFarmGroup, TopFarmProblem
from topfarm.easy_drivers import EasyRandomSearchDriver
from topfarm.drivers.random_search_driver import RandomizeTurbinePosition_Circle
from topfarm.constraint_components.boundary import CircleBoundaryConstraint
from topfarm.plotting import XYPlotComp, NoPlot
from topfarm.constraint_components.spacing import SpacingConstraint

from py_wake.examples.data.DTU10MW_RWT import DTU10MW
from py_wake.site import WaspGridSiteBase, UniformWeibullSite
from py_wake.site.shear import PowerShear
from topfarm.constraint_components.boundary import XYBoundaryConstraint


def get_site():
    f = [0.035972, 0.039487, 0.051674, 0.070002, 0.083645, 0.064348,
         0.086432, 0.117705, 0.151576, 0.147379, 0.10012, 0.05166]
    A = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
     9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
    k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
     2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
    ti = 0.001
    h_ref = 100
    alpha = .1
    site = UniformWeibullSite(f, A, k, ti, shear=PowerShear(h_ref=h_ref, alpha=alpha))
    spacing = 2000
    N = 5
    theta = 76 # deg
    dx = np.tan(np.radians(theta))
    x = np.array([np.linspace(0,(N-1)*spacing,N)+i*spacing/dx for i in range(N)])
    y = np.array(np.array([N*[i*spacing] for i in range(N)]))
    initial_positions = np.column_stack((x.ravel(),y.ravel()))
    eps = 2000
    delta = 5
    site.boundary = np.array([(0-delta, 0-delta),
                     ((N-1)*spacing+eps, 0-delta),
                     ((N-1)*spacing*(1+1/dx)+eps*(1+np.cos(np.radians(theta))), (N-1)*spacing+eps*np.sin(np.radians(theta))-delta),
                     ((N-1)*spacing/dx+eps*np.cos(np.radians(theta)), (N-1)*spacing+eps*np.sin(np.radians(theta)))])
    site.initial_position = initial_positions
    return site

def main():
    if __name__ == '__main__':
        plot_comp = XYPlotComp()
        site = get_site()
        n_wt = len(site.initial_position)
        windTurbines = DTU10MW()
        min_spacing = 2 * windTurbines.diameter(0)
        wake_model = IEA37SimpleBastankhahGaussian(site, windTurbines)
        Drotor_vector = [windTurbines.diameter()] * n_wt 
        power_rated_vector = [float(windTurbines.power(20)/1000)] * n_wt 
        hub_height_vector = [windTurbines.hub_height()] * n_wt 
        AEPCalc = AEPCalculator(wake_model)         

        def aep_func(x, y, **kwargs):
            return AEPCalc.calculate_AEP(x_i=x, y_i=y).sum(-1).sum(-1)*10**6
        
        def irr_func(aep, **kwargs):
            return economic_evaluation(Drotor_vector, power_rated_vector, hub_height_vector, aep).calculate_irr()
        
        aep_comp = CostModelComponent(input_keys=['x','y'], n_wt=n_wt, cost_function=aep_func, output_key="aep", output_unit="GWh", objective=False, output_val=np.zeros(n_wt))
        irr_comp = CostModelComponent(input_keys=['aep'],   n_wt=n_wt, cost_function=irr_func, output_key="irr", output_unit="%",   objective=True, income_model=True)
        group = TopFarmGroup([aep_comp, irr_comp])
        problem = TopFarmProblem(
                design_vars=dict(zip('xy', site.initial_position.T)),
                cost_comp=group,
                driver=EasyRandomSearchDriver(randomize_func=RandomizeTurbinePosition_Circle(), max_iter=50),
            constraints=[SpacingConstraint(min_spacing),
                         XYBoundaryConstraint(site.boundary),],
                plot_comp=plot_comp)
        cost, state, recorder = problem.optimize()

main()