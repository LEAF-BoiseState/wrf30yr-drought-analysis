import xarray as xr
import numpy as np
import sys


def FAO56(wrf_landmodel_file, wrf_forcing_file, wrf_surfrad_file, pet_output_file):

    ds_land = xr.open_dataset(wrf_landmodel_file)
    ds_atmo = xr.open_dataset(wrf_forcing_file)
    ds_surfrad = xr.open_dataset(wrf_surfrad_file)

    # Get variables needed to compute PET
    U = ds_atmo['U10_DM'].values # Zonal wind at 10 m, daily average
    V = ds_atmo['V10_DM'].values # Meridional wind at 10 m, daily average
    T2 = ds_atmo['T2_DV'].values # Temperature at 2 m, daily average
    Q2 = ds_atmo['Q2_DM'].values # Specific humidity at 2 m, daily average
    P = ds_atmo['PSFC_DM'].values # Surface pressure, daily average
    P = P / 1000.0 # Convert from Pa to kPa

    # Get the radiant fluxes
    SWdown = ds_surfrad['SWDOWN_DM'].values
    SWup = ds_surfrad['SWUPB_DM'].values
    LWdown = ds_surfrad['GLW_DM'].values
    LWup = ds_surfrad['LWUPB_DM'].values

    # Get the ground heat flux
    Gveg = ds_land['GHV_DM'].values
    Gsoi = ds_land['GHB_DM'].values
    Fv = ds_land['FVEG_DM'].values

    # Get latent heat flux from the model
    LH = ds_land['LH_DM'].values

    # Get coordinate variables to write to output
    XTIME = ds_land['XTIME'].values
    XLONG = ds_land['XLONG'].values
    XLAT = ds_land['XLAT'].values

    #=============================#
    # Calculate the net radiation #
    #=============================#
    Rnet = ((SWdown - SWup) + (LWdown - LWup)) # Rnet will be saved

    #============================#
    # Calculate ground heat flux #
    #============================#
    # Calculate the ground heat flux by multiplying the ground heat flux under canopy 
    # by the vegetation fraction and adding the ground heat flux of bare soil times  
    # one minus the vegetation fraction
    G = Gveg * Fv + (1.0 - Fv) * Gsoi

    #====================================#
    # Compute the Psychrometric Constant #
    #====================================#
    gamma = 0.665E-03 * P

    #==========================================================#
    # Compute the slope of the saturation vapor pressure curve #
    #==========================================================#
    T2C = T2 - 273.15
    Delta = (2504.0 * np.exp((17.27*T2C)/(T2C + 237.2)))/ (T2C + 237.2)**2.0

    #==================================#
    # Calculate Vapor Pressure Deficit #
    #==================================#
    # Calculate saturation and actual vapor pressure, and vapor pressure deficit
    ea = 0.622 * P * Q2 # Vapor pressure in kPa
    es = 0.611 * np.exp((17.27*T2C)/(T2C + 237.2)) # Saturation vapor pressure in kPa

    VPD = (es - ea) # VPD will be saved

    # Calculate wind speed and bring 10-meter wind-speed to 2-m consistent with temperature and humidity
    U10 = np.sqrt(U**2.0 + V**2.0) * 0.75
    U2 = U10 * 4.87 / np.log(67.8*10.0 - 5.42)

    #========================================#
    # Calculate Potential Evapotranspiration #
    #========================================#
    # Note the multiplication of (Rn - G) by 0.0864 to convert from W/m^2 to MJ/m^2/day
    
    PETnum = 0.408 * Delta * ((Rnet - G) * 0.0864) + (gamma * U2 * VPD) * (900.0 / (T2C + 273.0))
    PETden = Delta + gamma*(1 + 0.34*U2)

    PET = PETnum / PETden # Units are mm/day

    #===========================================================#
    # Calculate Actual Evapotranspiration from Latent Heat Flux #
    #===========================================================#
    aET = LH * (1.0/2.5E6) * (86400.0)

    #===========================#
    # Create the Output Dataset #
    #===========================#
    ds_pet = xr.Dataset(
        data_vars=dict(
            Rnet=(['XTIME','south_north','west_east'], Rnet),
            VPD=(['XTIME','south_north','west_east'], VPD),
            PET=(['XTIME','south_north','west_east'], PET),
            aET=(['XTIME','south_north','west_east'], aET),
        ),
        coords=dict(
            XTIME=(['XTIME'], XTIME),
            XLONG=(['XTIME','south_north','west_east'], XLONG),
            XLAT=(['XTIME','south_north','west_east'],XLAT)
        ),
        attrs=dict(description='PET estimated via FAO 56 method (Allen et al, 1998)'),
    )

    ds_pet['XLONG'].attrs = ds_land['XLONG'].attrs
    ds_pet['XLAT'].attrs = ds_land['XLAT'].attrs

    #===========================================#
    # Write the Output Dataset to a NetCDF File # 
    #===========================================#
    ds_pet.to_netcdf(pet_output_file)



