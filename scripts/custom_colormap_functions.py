"""
Functions for defining custom colormaps.
"""

# Python standard modules
import warnings

# Numerical modules
import numpy as np
from scipy.optimize import least_squares

# Color modules
import colorspacious as cs
import matplotlib.cm as cm
import matplotlib.colors as colors

# Piecewise linear perceptually uniform segments
def segment_uniform(anchors, samples_rgb1, name='segment_uniform', num_points=1024):

  # Prepare abscissas
  x = np.linspace(0.0, 1.0, num_points)

  # Convert samples to perceptually uniform space
  samples_jjab = cs.cspace_convert(samples_rgb1, 'sRGB1', cs.CAM02UCS)

  # Interpolate samples in perceptually uniform space
  jjp = np.interp(x, anchors, samples_jjab[:,0])
  ap = np.interp(x, anchors, samples_jjab[:,1])
  bp = np.interp(x, anchors, samples_jjab[:,2])
  jjab = np.hstack((jjp[:,None], ap[:,None], bp[:,None]))

  # Calculate RGB values
  with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'divide by zero encountered in true_divide', RuntimeWarning)
    rgb1 = cs.cspace_convert(jjab, cs.CAM02UCS, 'sRGB1')

  # Clip colors
  rgb1 = np.clip(rgb1, 0.0, 1.0)

  # Create colormap
  x_rgb1 = [(x_val, rgb1_val) for x_val, rgb1_val in zip(x, rgb1)]
  cmap = colors.LinearSegmentedColormap.from_list(name, x_rgb1)
  cm.register_cmap(name=name, cmap=cmap)
  return cmap

# Perceptually uniform helix
def helix_uniform(start_jjmmh, end_jjmmh, winding_num, name='helix_uniform', num_points=1024):

  # Parameters
  c1 = 0.007
  c2 = 0.0228
  hr_max_dev = np.pi / 4.0

  # Prepare abscissas
  x = np.linspace(0.0, 1.0, num_points)

  # Calculate endpoints in perceptually uniform space
  jj_start = start_jjmmh[0]
  jjp_start = (1.0 + 100.0 * c1) * jj_start / (1.0 + c1 * jj_start)
  mm_start = start_jjmmh[1]
  mmp_start = np.log(1.0 + c2 * mm_start) / c2
  h_start = start_jjmmh[2]
  hr_start = h_start * np.pi / 180.0
  jj_end = end_jjmmh[0]
  jjp_end = (1.0 + 100.0 * c1) * jj_end / (1.0 + c1 * jj_end)
  mm_end = end_jjmmh[1]
  mmp_end = np.log(1.0 + c2 * mm_end) / c2
  h_end = end_jjmmh[2]
  hr_end = h_end * np.pi / 180.0

  # Calculate regular helix
  jjp = np.linspace(jjp_start, jjp_end, num_points)
  mmp = np.linspace(mmp_start, mmp_end, num_points)
  hr = np.linspace(hr_start, hr_end + 2.0 * np.pi * winding_num, num_points)

  # Make helix uniform in color difference
  def res(hr_int_vals):
    hr_vals = np.concatenate(([hr[0]], hr_int_vals, [hr[-1]]))
    ap_vals = mmp * np.cos(hr_vals)
    bp_vals = mmp * np.sin(hr_vals)
    deep_vals = np.hypot(np.diff(jjp), np.hypot(np.diff(ap_vals), np.diff(bp_vals)))
    return deep_vals - np.mean(deep_vals)
  def jac(hr_int_vals):
    hr_vals = np.concatenate(([hr[0]], hr_int_vals, [hr[-1]]))
    ap_vals = mmp * np.cos(hr_vals)
    bp_vals = mmp * np.sin(hr_vals)
    deep_vals = np.hypot(np.diff(jjp), np.hypot(np.diff(ap_vals), np.diff(bp_vals)))
    jacobian = np.zeros((num_points - 1, num_points - 2))
    jacobian[0,0] = mmp[0] * mmp[1] / deep_vals[0] * np.sin(hr_vals[1] - hr_vals[0])
    for k in range(1, num_points - 2):
      jacobian[k,k-1] = mmp[k] * mmp[k+1] / deep_vals[k] * np.sin(hr_vals[k] - hr_vals[k+1])
      jacobian[k,k] = -jacobian[k,k-1]
    jacobian[-1,-1] = mmp[-2] * mmp[-1] / deep_vals[-1] * np.sin(hr_vals[-1] - hr_vals[-2])
    return jacobian
  jac_sparsity = np.zeros((num_points - 1, num_points - 2))
  jac_sparsity[0,0] = 1.0
  for k in range(1, num_points - 2):
    jac_sparsity[k,k-1:k+1] = 1.0
  jac_sparsity[-1,-1] = 1.0
  bounds = (hr[1:-1] - hr_max_dev, hr[1:-1] + hr_max_dev)
  sol = least_squares(res, hr[1:-1], jac=jac, bounds=bounds, jac_sparsity=jac_sparsity)
  hr = np.concatenate(([hr[0]], sol.x, [hr[-1]]))

  # Calculate RGB values
  ap = mmp * np.cos(hr)
  bp = mmp * np.sin(hr)
  jjab = np.hstack((jjp[:,None], ap[:,None], bp[:,None]))
  with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'divide by zero encountered in true_divide', RuntimeWarning)
    rgb1 = cs.cspace_convert(jjab, cs.CAM02UCS, 'sRGB1')

  # Clip colors
  rgb1 = np.clip(rgb1, 0.0, 1.0)

  # Create colormap
  x_rgb1 = [(x_val, rgb1_val) for x_val, rgb1_val in zip(x, rgb1)]
  cmap = colors.LinearSegmentedColormap.from_list(name, x_rgb1)
  cm.register_cmap(name=name, cmap=cmap)
  return cmap
