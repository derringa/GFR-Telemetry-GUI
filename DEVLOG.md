# GFR Telemetry GUI Changelog #
## Unfinished ##
## Next tasks ##
* Add click handlers to play and track buttons.
* Confirm with team what channels are needed to get steering wheel and tire angle changes.
* Find graphics for steering wheel to apply to main window.

## 11/21/2019 ##
* First design on main window layout.
* Main window displaying.
* Menu bar file and view drop downs added.
* Pop up window generation and value passing back to main window.

## 12/5/2019 ##
* Tab class creating containing a QTab and pyqtgraph plot.
* Pop up window passes user input to generate tabs each displaying graph data.

## 12/18/2019 ##
* Using asammdf to reach MF4 files but cannot extract data.

## 1/16/2020 ##
### DBC Files ###
* Import file path and extracting channel names from file.
* Feature desired so that channels can be picked before start of event.
* Added a Qlist with checkboxes that is populated by DBC channel names.
* (Un)checking boxes causes signal handling to add or remove channel names from desired channel list.
* Successful import enable MDF file import.
### MDF Files ###
* Import file path and extracting channel data using asammdf.
* Cross referencing expected channels from DBC - deletes those not present from checklist and desired channel list.
* Successful import enable plot data feature.
### Plot Data ###
* Compares current list of desired channels to those already generated as tabs/graphs - only graph newly checked channels.
* Deletes any graphs unchecked - no longer on the desired channels list.

## 1/21/2020 ##
### Graph signal events ###
* Learned different types of signal events associated with graph features.
* Added a horizontal tracking line to the graph that can be dragged along x-axis.
### Formatting ###
* Updated fixed sizes for side columns, leaving more room for graph information as window scales.

## 1/22/2020 ##
### Time Slider ###
* Added Qslider which, on (re)plot has value range rescaled from 0 to highest timestamp from all data.
* Included signal handler on marker change iterate through tab objects and change position of tracking line.
### Tab Class ###
* Is now passed reference to the GUI Qslider.
* Added signal handler upon tracking line move change marker of time slider to match the timestamps
* Upon this change the slider function then updates all other graph line.
### Time-Synchronization ###
* Now sliding any time tracking mechanisms keeps all others in track together.
