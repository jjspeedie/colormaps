#! /usr/bin/env python

"""
Script for extracting and saving data from GR torus simulation.
"""

# Python standard modules
import sys

# Other modules
import numpy as np

# Main function
def main():

  # Parameters
  read_dir = '/Users/cjwhite/codes/athena/vis/python'
  input_file = '/Users/cjwhite/research/athena_method/data/torus/s90_t00_high.prim.01000.athdf'
  output_file = '/Users/cjwhite/projects/colormaps/data/torus.npz'

  # Load data reader
  sys.path.insert(0, read_dir)
  import athena_read

  # Read data
  data_coord = athena_read.athdf(input_file, quantities=[])
  r = data_coord['x1v']
  rf = data_coord['x1f']
  th = data_coord['x2v']
  thf = data_coord['x2f']
  nph = len(data_coord['x3v'])
  dph = 2.0 * np.pi / nph
  ph_min = 1.0 / 3.0 * dph
  ph_max = 2.0 / 3.0 * dph
  data_right = athena_read.athdf(input_file, quantities=('rho',), x3_min=ph_min, x3_max=ph_max)
  ph_min = np.pi + 1.0 / 3.0 * dph
  ph_max = np.pi + 2.0 / 3.0 * dph
  data_left = athena_read.athdf(input_file, quantities=('rho',), x3_min=ph_min, x3_max=ph_max)

  # Calculate grids
  th_ext = np.concatenate((th, 2.0 * np.pi - th[::-1]))
  thf_ext = np.concatenate((th, 2.0 * np.pi - thf[-1::-1]))
  xf = rf[None,:] * np.sin(thf_ext[:,None])
  yf = rf[None,:] * np.cos(thf_ext[:,None])

  # Assemble cell quantities
  rho = np.vstack((data_right['rho'], data_left['rho'][::-1,:]))

  # Assemble data
  data_out = {}
  data_out['xf'] = xf
  data_out['yf'] = yf
  data_out['rho'] = rho

  # Save data
  np.savez(output_file, **data_out)

# Execute main function
if __name__ == '__main__':
  main()
