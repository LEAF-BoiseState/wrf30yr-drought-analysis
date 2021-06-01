import ComputeDaily_PET
import numpy as np



for wy in np.arange(1987,2018):

    wrf_output_dir = '/Volumes/G-SPEED Shuttle XL/wrf-30yr-daily/'
    wrf_landmodel_file = wrf_output_dir+'landmodel_d01_wy'+str(wy)+'_daily_summary.nc'
    wrf_forcing_file = wrf_output_dir+'forcing_d01_wy'+str(wy)+'_daily_summary.nc'
    wrf_surfrad_file = wrf_output_dir+'surfrad_d01_wy'+str(wy)+'_daily_summary.nc'

    pet_outfile = './pet_d01_wy'+str(wy)+'_daily.nc'

    ComputeDaily_PET.FAO56(wrf_landmodel_file, wrf_forcing_file, wrf_surfrad_file, pet_outfile)

    print('Completed computing PET for water year '+str(wy))

    