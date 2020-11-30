import random
import json
import numpy as np
import matplotlib.pyplot as plt
from blimpy import Waterfall
from astropy.coordinates import Angle
import astropy.units as u

ntotal = 400
n_frbs = 119
category = open("/mnt/buf0/furbies_for_helen/furbies_run_1/furbies.cat", "rb")
#skipping header
for i in range(4):
    category.readline()
id_set = []
for i in range(ntotal):
    fid = category.readline()[0:4]
    id_set.append(fid.decode("utf-8"))
selected_frbs = random.sample(id_set, n_frbs)
with open("TOP_SECRET.txt","w") as f:
    json.dump(selected_frbs, f)

#load in noise
fb = Waterfall('ics_a.fil', max_load=10)
plotf, plotdata = fb.grab_data()
plotdata=plotdata.transpose()
#noisedata = plotdata[:, 0:16000]

NSAMPLES = 16000
NCHANS = 4096
HDR_SIZE = 16384
DTYPE = np.float32

frbs=[]

def inject(noise, frbs, nsample, interval):
    for i in range(len(frbs)):
        print(i)
        fname = "/mnt/buf0/furbies_for_helen/furbies_run_1/furby_"+frbs[i]
        o = open(fname, "rb")
        hdr = o.read(HDR_SIZE)
        data = np.fromfile(o, dtype=DTYPE).reshape(NSAMPLES, NCHANS).T*10/7
        data = data+np.random.uniform(-0.5,0.5,data.shape)
        start = i*interval
        noise_seg = noise[:,start:start+nsample]
        #scaling
        new_data = np.add(noise_seg, data)
        #handling overflow and casting the final data after adding
        new_data[new_data>255] = 255
        noise[:,start:start+nsample] = new_data.round().astype(np.uint8)
    return noise
interval = int(10/(480*1e-6))
inj = inject(plotdata, selected_frbs, NSAMPLES, interval)

h = {}
h['az_start'] = 0.0
h['data_type'] = 1
h['fch1'] = 2112.125
h['foff'] = -0.25
h['ibeam'] = 0
h['machine_id'] = 0
h['nbeams'] = 1
h['nbits'] = 8
h['nchans'] = 4096
h['nifs'] = 1
h['rawdatafile'] = "N/A"
h['source_name'] = "frb180916"
h['src_dej'] = Angle("65.73439581", unit=u.deg)
h['src_raj'] = Angle("1.96651447", unit = u.hour)
h['telescope_id'] = 0
h["tsamp"] = 0.00048
h['tstart'] = 59144.711759259255
h['za_start'] = 0.0
fb.header = h

fb.data = inj.T
fb.write_to_fil("frbs.fil")
plt.imshow(inj[:,0:50000], interpolation = 'nearest', aspect = 'auto')
plt.show()
