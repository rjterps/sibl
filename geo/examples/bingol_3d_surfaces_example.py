# bingol_3d_surfaces.py
# Example useage:
# $ conda activate nurbspyenv
# $ python bingol_3d_surfaces.py

from geomdl import BSpline
from geomdl.visualization import VisMPL as vis

surf = BSpline.Surface()
surf.degree_u = 3
surf.degree_v = 2
control_points = [
    [0, 0, 0],
    [0, 4, 0],
    [0, 8, -3],
    [2, 0, 6],
    [2, 4, 0],
    [2, 8, 0],
    [4, 0, 0],
    [4, 4, 0],
    [4, 8, 3],
    [6, 0, 0],
    [6, 4, -3],
    [6, 8, 0],
]
surf.set_ctrlpts(control_points, 4, 3)
surf.knotvector_u = [0, 0, 0, 0, 1, 1, 1, 1]
surf.knotvector_v = [0, 0, 0, 1, 1, 1]

# surf.delta = 0.05
surf.delta = 0.20  # 0.20 for testing, was originally 0.05 for smoothness

# 0.20, with 1.0 / 0.20 = 5.0,
# gives a matrix of [5x5] evalution points found by > surf.evalpts

# surf.vis = vis.VisSurface()
surf.vis = vis.VisSurface(vis.VisConfig(alpha=0.8))

surface_points = surf.evalpts
print(surface_points)
surf.render()

# surface 2, to come.
