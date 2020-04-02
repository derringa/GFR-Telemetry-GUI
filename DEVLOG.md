# GFR Telemetry GUI Changelog #
## Unfinished/Dysfunctional ##

## Tasks (By Priority) ##
* Find graphics for steering wheel to apply to main window, rotate paint event on time change.
* Track minimap using GPS data.
* Convert unit measurements for data being displayed.
* Customize plot line colors.
* Drag and drop signals from main window list into graphs.

## Design Questions ##
* Do we want to display yaw, roll, pitch, acceleration in x/y/z etc. visually?
* GPS data not extrapolating as expected. Needed to develop track visualization.
* If track can be displayed, how are we designating a starting location and determining lap time?
* Previous DBC files did not specify group in provided field but in comment. Had to program to tokenize comment string. Change future DBC files?

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

## 1/25/2020 ##
### Asynchronous Play ###
* Added Qthreading of track play incrementation allowing the GUI to receive other inputs.
### Channel Navigation ###
* Added collapsible channel group names for easer channel navigation.

## 1/30/2020 ##
### Graph Behavior ###
* Locked vertical scrolling and max horizontal scrolling to largest range of plotted values.

## 3/10/2020 ##
### Custom Graphs ###
* Popup window to generate multiplot graph in tab widget.
* Custom title and plot data available.
* Plot generation asyncronous with data import. Prepare workspace before upload.

## 3/26/2020 ##
### Signal Management ###
* Redesign signal data structure to account for group name and place in dict.
* Reconfigure main window and popup to work with new dict format.

## 3/28/2020 ##
### Save/Load Workspace ###
* Save current configuration of tabs in a JSON file.
* Load JSON file and generate tabs asyncrounously with data import.

## 4/1/2020 ##
### Edit Workspace ###
* Previously developed add tab popup now populates with current selected tab graph data to be edited.
### Import Data ###
* Popup window for mdf and dbc file select generated. Validated and passed to main window.
### Toolbar ###
* Import data and managing tabs moved primarily to toolbar dropdown selections. Buttons removed.