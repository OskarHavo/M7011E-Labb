# M7011E Lab
Robin Danielsson and Oskar Havo

# Instruction for Audit
text

# Deployment Protocol
text

# Design Document
text

# Design Diagram
bild

# Data Model Specification
text och bild









# Features and Design Choices.
bild på alla kort

## Logic
### Basic
***Automated Tests*** <br>
**Oskar & Robin** <br>
Every relevant backend function pertaining to the Mathematical Model is tested using Python Testing. We have focused on testing for every case in the mathematical model rather than testing every network component due to time constraints. 


***Mathematical Model*** <br>
**Oskar & Robin** <br>
The windmill production was to gradually change, and thus we use a sine wave function in order to create realistic wind patterns. Inorder to simulate geographical differences we have a different sine wave phase depending on the Area Code. This aims to simulate the wind patterns moving through the area at different times due to their geographical seperation. To simulate realistic weather patterns we also have a function determining the households power consumption based on the month, making it such that the consumption is lower in the summer time and higher during winter. The powerplant produces a set number of kWh which is then balanced out to give each house the same amount of base power. The windmills can also get broken down for a random number of days and the power plants can experience blackouts to certain area codes.

The price is calculated through having a base price and then adding/subtracting a simple demand/suply quota. We also have a function which uses the settable buy/sell ratios enabling the saving/selling of power.


***RESTful API*** <br>
**Robin** <br>
robyn

### Advanced

***Historical Data*** <br>
**Robin** <br>
robyn


***Locational Data*** <br>
**Oskar** <br>
Inorder to simulate geographical differences we have a different sine wave phase depending on the Area Code. This aims to simulate the wind patterns moving through the area at different times due to their geographical seperation.

***Modelling with Realistic Outdoor Weather*** <br>
**Oskar** <br>
To simulate realistic weather patterns we also have a function determining the households power consumption based on the month, making it such that the consumption is lower in the summer time and higher during winter.

***Realistic Wind Turbines*** <br>
**Oskar** <br>
The windmills can also get broken down for a random number of days. During this time the household only recieves energy from the Power Plant and from its energy buffer.



## User
### Basic

***Coal Powerplant Graphical Tools*** <br>
**Oskar** <br>
We have implemented gauges, sliders and graphs to allow the admin to visualize, manipulate and assess the energy data. 

***Controlling Ratio of Buying/Stored Energy*** <br>
**Oskar** <br>
By using using the sliders in the web interface you can control the ratio.

***Controlling Ratio of Selling/Storing Energy*** <br>
**Oskar** <br>
By using using the sliders in the web interface you can control the ratio.


***Login/Logout*** <br>
**Robin** <br>
robyn

***Upload House Photo*** <br>
**Robin** <br>
robyn


***Viewable Data*** <br>
**Oskar** <br>
All the required data is displayed in raw form, graph form and most extensively in our gauges.

### Advanced
***Account Deletion / Change Info*** <br>
**Oskar & Robin** <br>
robyn


***Multiple Logins*** <br>
**Robin** <br>
robyn


***Reorder Gagues with Drag and Drop*** <br>
**Oskar** <br>
We have implemented draggable gauges based on an example in order to easily visualize the data and to allow the user to change the order as it deems fit.

***User Friendly Data View (Gauges)*** <br>
**Oskar** <br>
We have implemented draggable gauges based on an example in order to easily visualize the data and to allow the user to change the order as it deems fit.


## Admin
### Basic

***Account Deletion / Change Info of Other Users*** <br>
**Oskar & Robin** <br>
robyn



***Coal Plant Energy Production Demand*** <br>
**Oskar** <br>
The Coal Plant Energy Production is displayed in one of our gauges.


***Coal Plant Status** <br>
**Oskar & Robin** <br>
The Coal Plant Status is displayed in one of our gauges. When the simulation starts it will be "Starting" for 10 timesteps and then go to "Running".


***Electricity Price*** <br>
**Oskar** <br>
The electricity price can be set independently of the modelled electricity price. This price is then what is shown to the users.


***List of Prosumers*** <br>
**Oskar & Robin** <br>
The admin has a large table showing all users which allows for every action as requested.



***Market Demand*** <br>
**Oskar** <br>
The market demand is displayed in one of our gauges. It is calculated as described in the Mathematical Model section.


***Modelled Electricity Price*** <br>
**Oskar** <br>
The Modelled Electricity Priceis displayed in one of our gauges. It is calculated as described in the Mathematical Model section.


***Ratio of Buffer/Market*** <br>
**Oskar** <br>
By using using the sliders in the web interface you can control the ratio.

***Users Effected By Blackout*** <br>
**Oskar & Robin** <br>
Theh admin can see in its prosumer table the blackout status of each user.


### Advanced

***Coal Powerplant Graphical Tools*** <br>
**Oskar** <br>
We have implemented gauges, sliders and graphs to allow the admin to visualize, manipulate and assess the energy data. 

***IP and PORT Info*** <br>
**Oskar & Robin** <br>
The IP and PORT data is extracted from Flask and then displayed in the admins prosumer table.

***Real Time Data Stream*** <br>
**Robin** <br>
robyn

***Reorder Gagues with Drag and Drop*** <br>
**Oskar** <br>
We have implemented draggable gauges based on an example in order to easily visualize the data and to allow the user to change the order as it deems fit.



***Simulataneous Usage Across Different Devices*** <br>
**Robin** <br>
robyn



***Streaming Over Socket*** <br>
**Robin** <br>
robyn








# Authentication Design
dd


# Time Log
Robin Danielsson: n Hours Total
<br>
Oskar Havo: n+1 Hours Total
