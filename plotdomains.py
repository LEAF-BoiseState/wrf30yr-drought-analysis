
import xarray as xr
import os.path
#import math
#import numpy as np
import sys
import getopt
   
template_domains="""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Style id="transBluePoly">
      <LineStyle>
        <width>1.5</width>
      </LineStyle>
      <PolyStyle>
        <color>7dff0000</color>
      </PolyStyle>
    </Style>
    XPLACEMARKX
  </Document>
</kml>
"""

template_placemark="""<Placemark>
        <name>XDOMAINX</name>
        <visibility>1</visibility>
        <LineString>
          <tessellate>1</tessellate>
          <coordinates>
XCOORDSX
          </coordinates>
        </LineString>
      </Placemark>"""

class Usage(Exception):
   def __init__(self, msg):
      self.msg = msg
      
def usage():
   
    print('Usage: python plotdomains.py')

    print('Options:')

    print('-h or --help:     Prints this message')
    print('-o or --output=   The name of the output file (default=domains.kml)')
    print('-d or --ncdir=    Where the geo_em.* files are found (./)')
    print('--step=           The space between each point to use for drawing (20)')
        
def main(argv=None):
   
   ncdir='.'
   step=20
   output='domains.kml'
   
   if argv is None: argv=sys.argv
   
   try:
      try:
         opts, args = getopt.getopt(argv[1:], "ho:d:",\
                                    ["help","output=","step=","ncdir="])
      except getopt.error as msg:
             raise Usage(msg)
      # more code, unchanged
      for o,a in opts:
         if o in ('-h','--help'):
            usage()
         elif o in ('-o','--output'):
            output=a
         elif o == '--step':
            step=a
         elif o in ('-d','--ncdir'):
            ncdir=a
         else:
            assert False, "unhandled option"
  
   except Usage as err:
      print >>sys.stderr, err.msg
      print >>sys.stderr, "for help use --help"
      return 2
   
   args=sys.argv   
   
   pstr=""
   fn=ncdir+"/geo_em.d01.nc"

    
   ds = xr.open_dataset(fn)

   lon=ds['XLONG_M'][0,:,:]
   sz=lon.shape
   lat=ds['XLAT_M'][0,:,:]
   S='nlat: %03d, nlon: %03d' %(sz[0],sz[1])
   print("-->"+S)
   M=[]
   M.extend(zip(lon[0,::step],lat[0,::step]))
   M.extend(zip(lon[::step,-1],lat[::step,-1]))
   M.extend(zip(lon[-1,::-step],lat[-1,::-step]))
   M.extend(zip(lon[::-step,0],lat[::-step,0]))
   M.append(M[0]) # close the loop
   L="\n".join(["%.5f,%.5f" %tuple(elem) for elem in M])
   #print(L)
   a=template_placemark
   a=a.replace("XCOORDSX",L)
   a=a.replace("XDOMAINX",S)
   pstr+=a

   ds.close()

   
   a=template_domains
   a=a.replace("XPLACEMARKX",pstr)
   fid=open(ncdir+'/'+output,'w')
   fid.write(a)
   fid.close()
   
if __name__ == "__main__":
   sys.exit(main())

