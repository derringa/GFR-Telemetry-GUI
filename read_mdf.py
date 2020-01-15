from asammdf import MDF

mdf_file = "./2018-07-01_15-58-05Ehingen.mf4"
dbc_file = "./BCU.dbc"

mdf = MDF(mdf_file)
mdf_scaled = mdf.extract_can_logging(dbc_file, ignore_invalid_signals=True)
pd = mdf_scaled.to_dataframe(time_as_date=True)

print(pd)