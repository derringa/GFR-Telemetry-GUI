from asammdf import MDF
from pyqtgraph import plot

mdf_path = "./2018-07-01_15-58-05Ehingen.mf4"
dbc_path = ["./Vehicle_CAN.dbc"]

mdf_file = MDF(mdf_path)
mdf_extracted = mdf_file.extract_can_logging(dbc_path)

for sig in mdf_extracted.iter_channels():

    print("Signal: {} in Unit: {}".format(sig.name, sig.unit))
#     print("Samples: {}".format(sig.samples))
#     print("Timestamps: {}".format(sig.timestamps))

#mdf_extracted.get('Giga_Sweep_Mode').plot()

#dist = mdf_extracted.get('Driven_Distance_m')

# print("Signal: {} in Unit: {}".format(dist.name, dist.unit))
# print("Samples: {}".format(dist.samples))
# print("Timestamps: {}".format(dist.timestamps))

#plot(dist)