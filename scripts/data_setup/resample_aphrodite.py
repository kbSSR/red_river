'''
Script to resample APHRODITE grids with cdo.
'''

from esd.util import buffer_cdo_lonlat_grid_cfg
import esd
import numpy as np
import os
import pandas as pd
import subprocess
import xarray as xr

if __name__ == '__main__':
    
    ############################################################################
    # Create CDO grid configuration with a 6 degree buffer around the default
    # Red River 1 deg grid.
    ############################################################################
    fpath_cdo_grid_red_river = os.path.join(esd.cfg.path_data_bbox, 'cdo_grid_1deg_red_river')
    grid_cfg = buffer_cdo_lonlat_grid_cfg(fpath_cdo_grid_red_river, buf=6)
    fpath_cdo_red_river_6buf = os.path.join(esd.cfg.path_data_bbox,
                                            'cdo_grid_1deg_red_river_6degbuf')
    with open(fpath_cdo_red_river_6buf, 'w') as f:
        f.writelines(grid_cfg)
    ############################################################################
    
    ############################################################################
    # Downsample from native 0.25deg to 1deg buffered Red River GCM grid
    ############################################################################
    def downsample_cdo(fpath_in, fpath_out):
        cmd = "cdo remapcon,%s %s %s"%(fpath_cdo_red_river_6buf, fpath_in, fpath_out)
        print cmd
        subprocess.call(cmd, shell=True)
    fpath_out_1deg_prcp = os.path.join(esd.cfg.path_aphrodite_resample,
                                       'aprhodite_redriver_pcp_1961_2007_1deg_6degbuf.nc')
    downsample_cdo(esd.cfg.fpath_aphrodite_prcp, fpath_out_1deg_prcp)
    
    fpath_out_1deg_tair = os.path.join(esd.cfg.path_aphrodite_resample,
                                       'aprhodite_redriver_sat_1961_2007_1deg_6degbuf.nc')
    downsample_cdo(esd.cfg.fpath_aphrodite_tair, fpath_out_1deg_tair)
    ############################################################################
    
    ############################################################################
    # Upsample 1deg downsampled grids to Red River 0.25deg Aphrodite grid with
    # bicubic or bilinear interpolation (remapbil or remapbic)
    # These are used in the analog downscaling procedure
    ############################################################################
    fpath_cdo_grid_def = os.path.join(esd.cfg.path_data_bbox, 'cdo_grid_p25deg_red_river')
    def upsample_cdo(fpath_in, fpath_out, method='remapbil'):
        cmd = "cdo %s,%s %s %s"%(method, fpath_cdo_grid_def, fpath_in, fpath_out)
        print cmd
        subprocess.call(cmd, shell=True)
    resample_method = 'remapbic'
    fpath_out_p25deg_prcp = os.path.join(esd.cfg.path_aphrodite_resample,
                                         'aprhodite_redriver_pcp_1961_2007_p25deg_%s.nc'%resample_method)
    upsample_cdo(fpath_out_1deg_prcp, fpath_out_p25deg_prcp, method=resample_method)
    fpath_out_p25deg_tair = os.path.join(esd.cfg.path_aphrodite_resample,
                                         'aprhodite_redriver_sat_1961_2007_p25deg_%s.nc'%resample_method)
    upsample_cdo(fpath_out_1deg_tair, fpath_out_p25deg_tair, method=resample_method)
    ############################################################################
    
    ############################################################################
    # Created a version of Aphrodite cropped to the Red River 
    ############################################################################
    fpath_cdo_grid_def = os.path.join(esd.cfg.path_data_bbox, 'cdo_grid_p25deg_red_river')
    
    fpath_crp_prcp = os.path.join(esd.cfg.path_aphrodite_resample,
                                  'aprhodite_redriver_pcp_1961_2007_p25deg.nc')
    fpath_crp_tair = os.path.join(esd.cfg.path_aphrodite_resample,
                                  'aprhodite_redriver_sat_1961_2007_p25deg.nc')
    cmd_prcp = "cdo remapnn,%s %s %s"%(fpath_cdo_grid_def, esd.cfg.fpath_aphrodite_prcp,
                                       fpath_crp_prcp)
    cmd_tair = "cdo remapnn,%s %s %s"%(fpath_cdo_grid_def, esd.cfg.fpath_aphrodite_tair,
                                       fpath_crp_tair)

    # Modify time coordinate variable

    def convert_times(ds):
    
        times = pd.to_datetime(ds.time.to_pandas().astype(np.str),
                               format='%Y%m%d', errors='coerce')        
        return times.values

    ds_prcp = xr.open_dataset(fpath_crp_prcp).load()
    ds_prcp['time'] = convert_times(ds_prcp)
    ds_prcp.close()
    ds_prcp.to_netcdf(fpath_crp_prcp)
    
    ds_tair = xr.open_dataset(fpath_crp_tair).load()
    ds_tair['time'] = convert_times(ds_tair)
    ds_tair.close()
    ds_tair.to_netcdf(fpath_crp_tair)
    
    