



import xarray
import cfgrib
import glob
import os


#where the NBM grib files are
datadir='/Volumes/SSD/Users/Travis/Programs/Air/python3/grib_to_zarr/NBM'
#name of the NBM grib files to convert
files='*grib2'
#output directory for zarr files
outdir='/Volumes/SSD/Users/Travis/Programs/Air/python3/grib_to_zarr/NBM_zarr'
#concatenated grib file; no need to change
master_grib='out.grib' 

def main():
    concat()
    grib_to_zarr()


def concat():
    if not os.path.isfile(datadir+'/'+master_grib):
        print("Concatenating grib files")
        with open(datadir+'/'+master_grib,'wb') as outfile:
            for filename in glob.glob(datadir+'/'+files):
                with open(filename, "rb") as infile:
                    outfile.write(infile.read())



def grib_to_zarr():

    print("Converting gribs to zarr")
    #if output directory doesn't exist, create it
    if not os.path.exists(outdir):
        os.makedirs(outdir)


    alldata = cfgrib.open_datasets(datadir+'/'+master_grib,backend_kwargs={'read_keys': ['gridType']})

    for data in alldata:
        print("")
        
        for varname, da in data.data_vars.items():
            gribname = data[varname].attrs['long_name'] #long_name #GRIB_shortName
            gribname = gribname.replace(" ", ".")
            step = data[varname].attrs['GRIB_stepType']
            try: 
                level = data[varname].attrs['GRIB_typeOfLevel']
            except:
                level    = 'unknown'


            outfile = outdir + '/' + gribname+'_'+level+'_'+step
            
            print (outfile)
            d2 = data[varname].to_dataset()

            #without the load, rechunking on grib takes forever
            d2.load() 

            #now chunk
            #don't put chunking before load, otherwise it loads the whole dataset, takes forever
            if 'x' in data[varname].dims and 'y' in data[varname].dims and 'step' in data[varname].dims:
                d2 = d2.chunk({"x":150, "y":150, "step": -1}) 
            else:
                d2 = d2.chunk({"x":150, "y":150})

            d2.to_zarr(outfile+'.zarr',mode='w')
            d2.to_netcdf(outfile+'.nc',mode='w')



if __name__ == "__main__":
    main()

