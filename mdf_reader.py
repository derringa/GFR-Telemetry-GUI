from asammdf import MDF, Signal

mdf = MDF("./2018-07-01_15-58-05Ehingen.mf4")

for sig in mdf.iter_channels():
    print('Sig repr', sig)
    print('Samples and timestamps:', sig.samples, sig.timestamps)