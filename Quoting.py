import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import googlemaps
import requests
import json
import statistics
import holidays


api_key = 'AIzaSyD6W8IlU0bOU1xZCrQx3zD9UUkoQ6TU_Bk'
endpoint = 'https://routes.googleapis.com/directions/v2:computeRoutes'
pickup_mileage, pickup_estimated_toll, pickup_org_state, pickup_dest_state = 0,0,0,0
del_mileage, del_estimated_toll, del_org_state, del_dest_state= 0 ,0,0,0

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=api_key)

def calculate_mileage_and_tolls(origin, destination):

    # Use the directions API to get the route information
    directions = gmaps.directions(origin, destination, units='imperial', avoid='ferries')

    if directions:
        # Extract the distance from the route information
        distance = directions[0]['legs'][0]['distance']['text']

        # Check for tolls in route steps
        tolls_found = False
        for step in directions[0]['legs'][0]['steps']:
            if "toll" in step.get('html_instructions', '').lower():
                tolls_found = True
                break

        tolls = "Tolls found on this route." if tolls_found else "No tolls found on this route."

        # Get the latitude and longitude of origin and destination
        origin_lat = directions[0]['legs'][0]['start_location']['lat']
        origin_lng = directions[0]['legs'][0]['start_location']['lng']
        destination_lat = directions[0]['legs'][0]['end_location']['lat']
        destination_lng = directions[0]['legs'][0]['end_location']['lng']
        dest_state = directions[0]['legs'][0]['end_address'].split(',')[-2]
        org_state= directions[0]['legs'][0]['start_address'].split(',')[-2]

        # Separate origin and destination coordinates


    # # Define the request payload
    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_lng
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination_lat,
                    "longitude": destination_lng
                }
            }
        },
        "travelMode": "DRIVE",
        "extraComputations": ["TOLLS"],
        "routeModifiers": {
            "vehicleInfo": {
                "emissionType": "GASOLINE"
            },
            "tollPasses": [
                "US_MA_EZPASSMA",
                "US_WA_GOOD_TO_GO"
            ]
        }
    }
    # # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.travelAdvisory.tollInfo,routes.legs.travelAdvisory.tollInfo'
    }

    # # Make the POST request
    response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    response_json = response.json()

    # Print the response

    mileage = response_json['routes'][0]['distanceMeters'] / 1609.34  # Convert meters to miles
    try:
        estimated_toll = response_json['routes'][0]['legs'][0]['travelAdvisory']['tollInfo']['estimatedPrice'][0]
    except:
        estimated_toll = 0 

    return mileage, estimated_toll, dest_state, org_state

def extract_value(data):
    if not isinstance(data, dict):
        return 0

    try:
        units = int(data.get('units', 0))
        nanos = data.get('nanos', 0) / 1e9
        return units + nanos
    except (TypeError, ValueError):
        return 0




st.markdown(
    """
    <style>
    
    .sidebar .sidebar-content {
        background-color: #001f3f;
    }
    .sidebar .markdown-text-container {
        color: white;
    }
    /* Change the background color of the dropdown menu */
    .sidebar .stSelectbox div[role="button"] {
        background-color: #001f3f;
    }
    /* Change the text color of the dropdown options */
    .sidebar .stSelectbox option {
        color: blue;
    }
 
    .custom-header {
    font-size: 1.2em;
    font-weight: bold;}

    .blue-oval-box {
    border: 2px solid blue;
    border-radius: 20px;
    padding: 20px;
    margin: 10px 0;}



    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<h1 style="font-size:46px">Sterling Quoting Tool</h1>', unsafe_allow_html=True)



# Create a sidebar for inputs
with st.sidebar:

    st.sidebar.image("download.png", caption='', use_column_width=True)
    # Customer
    st.header("Customer")
    customer = st.selectbox("Select Customer", ["Netjets", "Bombardier","T11"], key="customer")

    st.header("Service")
    service = st.selectbox("Select Service", ["NFO", "NDO", "HFPU"], key="service")

    # Weight (integer in pounds)
    st.header("Weight (in pounds)")

    # Set the max weight based on service selection
    if service in ["NFO", "HFPU"]:
        max_weight = 100
    else:
        max_weight = 100000

    weight = st.number_input("Enter Weight", min_value=1, max_value=max_weight, step=1, key="weight")

    # Vehicle Type
    st.header("Vehicle Type")
    vehicle = st.selectbox("Select Vehicle", ["Car", "Van", "Truck"], key="vehicle")

    # Pickup Date and Time
    st.header("Pickup Date and Time")
    pickup_date = st.date_input("Select Pickup Date", key="pickup_date")
    pickup_time = st.time_input("Select Pickup Time", key="pickup_time")

    
    st.header("Pickup")
    pickup_address = st.text_input("Pickup Address", "Bombardier Des Plaines", key="Pickup Address")
    if service !='NDO':
        pickup_airport = st.selectbox("Pickup Airport Code", ["ORD","ATL", "LAX", "DFW", "DEN", "JFK", "SFO", "SEA", "LAS", "MCO", "EWR", "PHX", "IAH", "MIA", "BOS", "MSP", "FLL", "DTW", "CLT", "SLC", "SAN", "BWI", "MDW", "TPA", "PDX", "HNL", "IAD", "DAL", "STL", "HOU", "AUS", "OAK", "MCI", "RDU", "MSY", "SJC", "SNA", "PIT", "SMF", "RSW", "CLE", "CMH", "IND", "BNA", "SAT", "PBI", "BUF", "OGG", "ELP", "TUS", "OMA", "CHS", "GRR", "SDF", "JAX", "ORF", "DAY", "ROC", "TUL", "BOI", "GEG", "CRP", "SYR", "LEX", "FAT", "SBN", "ABQ", "PWM", "TYS", "TRI", "GSO", "HSV", "EVV", "BTR", "AVL", "FAR", "MHT", "SGF", "LIT", "XNA", "TLH", "BIL", "CAK", "SCE", "BMI", "GPT", "SPI", "MFE", "PIA", "GJT", "MLI", "CWA", "JLN", "SUX", "BPT", "FSD", "SWF","YUL", "YYZ", "YVR", "YYC", "YEG", "YOW", "YWG", "YHZ", "YYJ", "YQB"] 
, key="pickup_airport")
        pickup_airport = pickup_airport + ' Airport'
    else:
        pickup_airport = None


    st.header("Delivery")
    if service != "NDO":
        delivery_airport = st.selectbox("Delivery Airport Code", ["EWR","ATL", "LAX", "ORD", "DFW", "DEN", "JFK", "SFO", "SEA", "LAS", "MCO", "PHX", "IAH", "MIA", "BOS", "MSP", "FLL", "DTW", "CLT", "SLC", "SAN", "BWI", "MDW", "TPA", "PDX", "HNL", "IAD", "DAL", "STL", "HOU", "AUS", "OAK", "MCI", "RDU", "MSY", "SJC", "SNA", "PIT", "SMF", "RSW", "CLE", "CMH", "IND", "BNA", "SAT", "PBI", "BUF", "OGG", "ELP", "TUS", "OMA", "CHS", "GRR", "SDF", "JAX", "ORF", "DAY", "ROC", "TUL", "BOI", "GEG", "CRP", "SYR", "LEX", "FAT", "SBN", "ABQ", "PWM", "TYS", "TRI", "GSO", "HSV", "EVV", "BTR", "AVL", "FAR", "MHT", "SGF", "LIT", "XNA", "TLH", "BIL", "CAK", "SCE", "BMI", "GPT", "SPI", "MFE", "PIA", "GJT", "MLI", "CWA", "JLN", "SUX", "BPT", "FSD", "SWF","YUL", "YYZ", "YVR", "YYC", "YEG", "YOW", "YWG", "YHZ", "YYJ", "YQB"] 
, key="delivery_airport")
        delivery_airport = delivery_airport + ' Airport'
    else: 
        delivery_airport = None
    
    delivery_address = st.text_input("Delivery Address",'Keuhne Nagel Jersey city', key="Delivery Address")

    st.header("Dangerous Goods")
    dangerous_goods = st.selectbox("Are Dangerous Goods Included?", ["No", "Yes"], key="dangerous_goods")

    st.header("Overnight Hold")
    overnight_hold = st.selectbox("Overnight Hold", ["No", "Yes"], key="overnight_hold")

    st.header("GPS")
    GPS = st.selectbox("Was a GPS Used?", ["No", "Yes"], key="GPS")

    st.header("Pieces")
    pieces = st.selectbox("Pieces", ["1", "2","3","4"], key="pieces")    

    if service !='NDO':
        st.header("Flight Legs")
        Legs = st.selectbox("Legs", ["1", "2","3"], key="Legs")    
    else:
        Legs = None

    # st.header("Wait Time")
    # waittime = st.number_input("Enter Wait time", min_value=0, max_value= 300, step=1, key="waittime")

    # st.header("Attempt")
    # attempt = st.selectbox("Was there an Attempe?", ["No", "Yes"], key="attempt")

message_placeholder = st.empty()
quote_placeholder = st.empty()  # Placeholder for the quote

# Show the message "please fill out the sidebar" by default
message_placeholder.markdown("**Fill Out The Sidebar For Quote**")

# Initialize final_quote with a default value
final_quote = 0

calculate_button = st.sidebar.button("Calculate Total")

# Only calculate and display the total if the button is pressed
if calculate_button:


    # Clear the message from the placeholder
    message_placeholder.empty()

    if service == 'NDO':
        pickup_mileage, pickup_estimated_toll, pickup_org_state, del_dest_stat = calculate_mileage_and_tolls(pickup_address, delivery_address )
        del_estimated_toll = extract_value(pickup_estimated_toll)

    else:
        pickup_mileage, pickup_estimated_toll, pickup_org_state, pickup_dest_state = calculate_mileage_and_tolls(pickup_address, pickup_airport )

        del_mileage, del_estimated_toll, del_org_state, del_dest_stat = calculate_mileage_and_tolls(delivery_airport, delivery_address)

        del_estimated_toll = extract_value(del_estimated_toll)
        pickup_estimated_toll = extract_value(del_estimated_toll)

    GasPrices = [3.536,3.533,3.600,3.656]

    fuelSurchragedata = {
        'At Least': [0, 2.31, 2.51, 2.81, 3.06, 3.31, 3.61, 3.91, 3.21, 4.51, 4.81, 5.11, 5.41, 5.71, 6.01, 6.31, 6.61, 6.91, 7.21],
        'Less than': [2.3, 2.5, 2.8, 3.05, 3.3, 3.6, 3.9, 4.2, 4.5, 4.8, 5.1, 5.4, 5.7, 6, 6.3, 6.6, 6.9, 7.2, 7.5],
        'Fuel Surcharge %': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    }
    FS = pd.DataFrame(fuelSurchragedata)

    data = {
        "Customer": [customer],
        "Service": [service],
        "Weight": [weight],
        "Vehicle Type": [vehicle],
        "Pickup Date": [pickup_date],
        "Pickup Time": [pickup_time],
        "Pickup Address": [pickup_address],
        "Pickup Airport Code": [pickup_airport],
        "Delivery Airport Code": [delivery_airport],
        "Delivery Address": [delivery_address],
        "Dangerous Goods Included": [dangerous_goods],
        "Overnight Hold": [overnight_hold],
        "GPS": [GPS],
        "Pieces": [pieces],
        "Flight Legs": [Legs],
        "Pickup Mileage": [pickup_mileage],
        "Pickup Estimated Toll": [pickup_estimated_toll],
        "Pickup Origin State": [pickup_org_state],
        "Delivery Mileage": [del_mileage],
        "Delivery Estimated Toll": [del_estimated_toll],
        "Delivery Destination State": [del_dest_stat]
        
    }

    df = pd.DataFrame(data)

    # st.write(df)




    if customer == "Netjets":

        if service =="NFO":
            weight = pd.Series([weight])
            weightcharge = pd.cut(weight, bins=[1, 10, 25, 50, 70, 100], labels=[106.00, 126.00, 135.00, 156.00, 169.00], right=False)

            weight_charge_value = weightcharge.iloc[0]
            df["Weight Charge"] = weight_charge_value

        if service =="HFPU":
            weight = pd.Series([weight])
            weightcharge = pd.cut(weight, bins=[1, 10, 25, 50, 70, 100], labels=[92.00, 107.00, 116.00, 122.00, 127.00], right=False)

            weight_charge_value = weightcharge.iloc[0]
            df["Weight Charge"] = weight_charge_value

        if service =="NDO":
            weight = pd.Series([weight])
            def calculate_charge(weight):
                if weight <= 50:
                    return 41
                else:
                    return 41 + 17 * ((weight - 50) // 50 + 1)

            # Apply the function to the dataframe
            df['Weight Charge'] = weight.apply(calculate_charge)



        def calculate_vehicle_charge(row):
            excess_miles = max(0, row['Pickup Mileage'] - 20) + max(0,row['Delivery Mileage'] - 20)   # Calculate excess miles
            

            if row["Vehicle Type"] == 'Car':
                vehicle_charge = 1.82
                flat_charge = 0
            elif row["Vehicle Type"] == 'Van':
                vehicle_charge = 2.5
                flat_charge = 60
            elif row["Vehicle Type"] == 'Truck':
                vehicle_charge = 3.4
                flat_charge = 150
            else:
                vehicle_charge = 0  # Default charge if vehicle type is not recognized
                flat_charge = 0 

            return (vehicle_charge * excess_miles) + flat_charge

        df['Vehicle Charge'] = df.apply(calculate_vehicle_charge, axis=1)

        df["Pieces"] = df["Pieces"].astype(int)
        df['DG fee'] = np.where(df["Dangerous Goods Included"] == "No" , 0 , 103)
        df['Pieces Charge'] = np.where(df['Pieces'] > 1, (df['Pieces'] - 1) * 86, 0)

        averageGasPrice = statistics.mean(GasPrices)

        def get_fuel_surcharge(averageGasPrice):
            for index, row in FS.iterrows():
                if row['At Least'] <= averageGasPrice < row['Less than']:
                    return row['Fuel Surcharge %']

        df['FS percetage'] = get_fuel_surcharge(averageGasPrice) /100

        if service !='NDO':
            df['Toll charge'] = (df['Delivery Estimated Toll'] + df['Pickup Estimated Toll']) * 1.1
        else:
            df['Toll charge'] = del_estimated_toll *1.1

        df['Delivery Destination State'] = df['Delivery Destination State'].str[1:3]
        df['Pickup Origin State'] = df['Pickup Origin State'].str[1:3]
        df['Non-Contiguous'] = np.where((df['Delivery Destination State'].isin(['HI', 'AL'])) | (df['Pickup Origin State'].isin(['HI', 'AL'])), 60, 0)

        if service !='NDO':
            df["Flight Legs"] = df["Flight Legs"].astype(int)
            df['Airline Transfer Charge'] = np.where(df['Flight Legs'] > 1, 0, 0)
        else:
            df['Airline Transfer Charge'] = 0 

        df['Overnight Hold Charge'] = np.where(df["Overnight Hold"] == "No" , 0 , 44)

        df['Holiday Charge'] =0 
        df['Weekend Charge']=0
        df['AfterHours Charge']=0

        df['GPS Fee'] = np.where(df["GPS"] == "No" , 0 , 100)

        df['total_sum'] = df["Weight Charge"] + df['Vehicle Charge'] + df['DG fee'] + df['Pieces Charge'] + df['Toll charge'] + df['Overnight Hold Charge']  + df['Non-Contiguous'] + df['GPS Fee'] + df['Airline Transfer Charge'] 
        df['Fuel Surcharge'] = df['total_sum']* df['FS percetage']
        df['Security Surcharge'] = df['total_sum']* .06


        # add attempt, Wait time
        df['Final Quote'] = df["Weight Charge"] + df['Vehicle Charge'] + df['DG fee'] + df['Pieces Charge'] + df['Toll charge'] + df['Overnight Hold Charge']  + df['Non-Contiguous'] + df['GPS Fee'] + df['Airline Transfer Charge'] + df['Fuel Surcharge'] + df['Security Surcharge']
        final_quote = df['Final Quote'].iloc[0]
    
    if customer == "Bombardier":

        df['Delivery Destination State'] = df['Delivery Destination State'].str[1:3]
        df['Pickup Origin State'] = df['Pickup Origin State'].str[1:3]
        if service =="NFO":
            weight = pd.Series([weight])
            
            def calculate_charge(weight):
                # Check if Delivery Destination State or Pickup Origin State is AL or HI
                if df['Delivery Destination State'].iloc[0] in ['AL', 'HI'] or df['Pickup Origin State'].iloc[0] in ['AL', 'HI']:
                    base_charge = 185
                else:
                    base_charge = 112

                if weight <= 50:
                    return base_charge
                else:
                    return base_charge + 20 * ((weight - 50) // 50 + 1)

            # Apply the function to the dataframe
            df['Weight Charge'] = weight.apply(calculate_charge)

        if service =="HFPU":
            def calculate_charge(weight):
                    
                if df['Delivery Destination State'].iloc[0] in ['AL', 'HI'] or df['Pickup Origin State'].iloc[0] in ['AL', 'HI']:
                    base_charge = 160
                else:
                    base_charge = 109
            
                    if weight <= 50:
                        return base_charge
                    else:
                        return base_charge + 20 * ((weight - 50) // 50 + 1)

                # Apply the function to the dataframe
            df['Weight Charge'] = weight.apply(calculate_charge)

        if service =="NDO":
            df['Airline Transfer Charge']= 0

            weight = pd.Series([weight])
            def calculate_charge(weight):
                if df['Delivery Destination State'].iloc[0] in ['KS', 'IL'] and df['Pickup Origin State'].iloc[0] in ['KS', 'IL']:
                     base_charge = 1599.84
                     return base_charge
     


                elif df['Delivery Destination State'].iloc[0] in ['AL', 'HI'] or df['Pickup Origin State'].iloc[0] in ['AL', 'HI']:
                    base_charge = 80
                else:
                    base_charge = 47


                if weight <= 50:
                    return base_charge
                else:
                    return base_charge + 20 * ((weight - 50) // 50 + 1)
                


            # Apply the function to the dataframe
            df['Weight Charge'] = weight.apply(calculate_charge)



        def calculate_vehicle_charge(row):
            excess_miles = max(0, row['Pickup Mileage'] - 30) + max(0,row['Delivery Mileage'] - 30)   # Calculate excess miles
            

            if row["Vehicle Type"] == 'Car':
                vehicle_charge = 2.0
                flat_charge = 0
            elif row["Vehicle Type"] == 'Van':
                vehicle_charge = 2.0
                flat_charge = 0
            elif row["Vehicle Type"] == 'Truck':
                vehicle_charge = 2.0
                flat_charge = 0
            else:
                vehicle_charge = 0  # Default charge if vehicle type is not recognized
                flat_charge = 0 

            return (vehicle_charge * excess_miles) + flat_charge

        df['Vehicle Charge'] = df.apply(calculate_vehicle_charge, axis=1)

        df["Pieces"] = df["Pieces"].astype(int)
        df['DG fee'] = np.where(df["Dangerous Goods Included"] == "No" , 0 , 95)
        df['Pieces Charge'] = np.where(df['Pieces'] > 1, 0, 0)

        averageGasPrice = statistics.mean(GasPrices)

        def get_fuel_surcharge(averageGasPrice):
            for index, row in FS.iterrows():
                if row['At Least'] <= averageGasPrice < row['Less than']:
                    return row['Fuel Surcharge %']

        df['FS percetage'] = get_fuel_surcharge(averageGasPrice) /100

        if service !='NDO':
            df['Toll charge'] = (df['Delivery Estimated Toll'] + df['Pickup Estimated Toll']) * 1.1
        else:
            df['Toll charge'] = del_estimated_toll * 0

        df['Holiday Charge'] =0 
        df['Weekend Charge']=0
        df['AfterHours Charge']=0

        if service !='NDO':
            df["Flight Legs"] = df["Flight Legs"].astype(int)

            condition_1 = df['Flight Legs'].iloc[0] > 1
            condition_2 = (df['Delivery Destination State'].iloc[0] in ['AL', 'HI']) or (df['Pickup Origin State'].iloc[0] in ['AL', 'HI'])
            condition_3 = df['Flight Legs'].iloc[0] == 1

            # Calculate the extra charge for weight over 50 lbs
            if condition_1:
                weight_increment = np.maximum(0, df['Weight'] - 50) // 1  # This will give the number of increments over 50 lbs
                weight_charge = 90 * weight_increment
            else:
                weight_charge = 0

            # Combine the conditions for the base charge
            base_charge = np.where((condition_1 & condition_2), 170, np.where(condition_1, 113, np.where(condition_3, 0, 0)))

            # Combine the base charge with the weight charge
            df['Airline Transfer Charge'] = base_charge + weight_charge
    

        df['Non-Contiguous']=0
        df['Overnight Hold Charge'] = np.where(df["Overnight Hold"] == "No" , 0 , 50)

        df['GPS Fee'] = np.where(df["GPS"] == "No" , 0 , 100)

        df['total_sum'] = df["Weight Charge"] + df['Vehicle Charge'] + df['DG fee'] + df['Pieces Charge'] + df['Toll charge'] + df['Overnight Hold Charge']  + df['Non-Contiguous'] + df['GPS Fee'] + df['Airline Transfer Charge'] 
        df['Fuel Surcharge'] = df['total_sum']* .25
        df['Security Surcharge'] = df['total_sum']* .06


        # add attempt, Wait time
        df['Final Quote'] = df["Weight Charge"] + df['Vehicle Charge'] + df['DG fee'] + df['Pieces Charge'] + df['Toll charge'] + df['Overnight Hold Charge']  + df['Non-Contiguous'] + df['GPS Fee'] + df['Airline Transfer Charge'] + df['Fuel Surcharge'] + df['Security Surcharge']
        final_quote = df['Final Quote'].iloc[0]

    if customer == "T11":

        df['Delivery Destination State'] = df['Delivery Destination State'].str[1:3]
        df['Pickup Origin State'] = df['Pickup Origin State'].str[1:3]
        if service =="NFO":
            weight = pd.Series([weight])
            
            def calculate_charge(weight):
                # Check if Delivery Destination State or Pickup Origin State is AL or HI
                if df['Delivery Destination State'].iloc[0] in ['AL', 'HI'] or df['Pickup Origin State'].iloc[0] in ['AL', 'HI']:
                    base_charge = 235
                else:
                    base_charge = 155

                if weight <= 50:
                    return base_charge
                else:
                    return base_charge + 25 * ((weight - 50) // 50 + 1)

            # Apply the function to the dataframe
            df['Weight Charge'] = weight.apply(calculate_charge)

        if service =="HFPU":
            def calculate_charge(weight):
                    
                if df['Delivery Destination State'].iloc[0] in ['AL', 'HI'] or df['Pickup Origin State'].iloc[0] in ['AL', 'HI']:
                    base_charge = 205
                else:
                    base_charge = 130
            
                    if weight <= 50:
                        return base_charge
                    else:
                        return base_charge + 25 * ((weight - 50) // 50 + 1)

                # Apply the function to the dataframe
            df['Weight Charge'] = weight.apply(calculate_charge)

        if service =="NDO":
            weight = pd.Series([weight])
            def calculate_charge(weight):

                if df['Delivery Destination State'].iloc[0] in ['AL', 'HI'] or df['Pickup Origin State'].iloc[0] in ['AL', 'HI']:
                    base_charge = 85
                else:
                    base_charge = 55


                if weight <= 50:
                    return base_charge
                else:
                    return base_charge + 25 * ((weight - 50) // 50 + 1)
                


            # Apply the function to the dataframe
            df['Weight Charge'] = weight.apply(calculate_charge)



        def calculate_vehicle_charge(row):
            excess_miles = max(0, row['Pickup Mileage'] - 15) + max(0,row['Delivery Mileage'] - 15)   # Calculate excess miles
            

            if row["Vehicle Type"] == 'Car':
                vehicle_charge = 2.75
                flat_charge = 0
            elif row["Vehicle Type"] == 'Van':
                vehicle_charge = 2.75
                flat_charge = 0
            elif row["Vehicle Type"] == 'Truck':
                vehicle_charge = 2.75
                flat_charge = 0
            else:
                vehicle_charge = 0  # Default charge if vehicle type is not recognized
                flat_charge = 0 

            return (vehicle_charge * excess_miles) + flat_charge

        df['Vehicle Charge'] = df.apply(calculate_vehicle_charge, axis=1)

        df["Pieces"] = df["Pieces"].astype(int)
        df['DG fee'] = np.where(df["Dangerous Goods Included"] == "No" , 0 , 200)
        df['Pieces Charge'] = np.where(df['Pieces'] > 1, 100, 0)

        averageGasPrice = statistics.mean(GasPrices)

        def get_fuel_surcharge(averageGasPrice):
            for index, row in FS.iterrows():
                if row['At Least'] <= averageGasPrice < row['Less than']:
                    return row['Fuel Surcharge %']

        df['FS percetage'] = get_fuel_surcharge(averageGasPrice) /100

        if service !='NDO':
            df['Toll charge'] = (df['Delivery Estimated Toll'] + df['Pickup Estimated Toll']) * 1.1
        else:
            df['Toll charge'] = del_estimated_toll * 0


        if service !='NDO':
            df["Flight Legs"] = df["Flight Legs"].astype(int)

            condition_1 = df['Flight Legs'].iloc[0] > 1
            condition_2 = (df['Delivery Destination State'].iloc[0] in ['AL', 'HI']) or (df['Pickup Origin State'].iloc[0] in ['AL', 'HI'])
            condition_3 = df['Flight Legs'].iloc[0] == 1

            # Calculate the extra charge for weight over 50 lbs
            if condition_1:
                weight_increment = np.maximum(0, df['Weight'] - 50) // 1  # This will give the number of increments over 50 lbs
                weight_charge = 25 * weight_increment
            else:
                weight_charge = 0

            # Combine the conditions for the base charge
            base_charge = np.where((condition_1 & condition_2), 210, np.where(condition_1, 140, np.where(condition_3, 0, 0)))

            # Combine the base charge with the weight charge
            df['Airline Transfer Charge'] = base_charge + weight_charge
    

        df['Non-Contiguous']=0
        df['Overnight Hold Charge'] = np.where(df["Overnight Hold"] == "No" , 0 , 50)

        df['GPS Fee'] = np.where(df["GPS"] == "No" , 0 , 0)

        df['Pickup Date'] = pd.to_datetime(df['Pickup Date'])

        # Initialize 'Holiday Charge' and 'Weekend Charge' columns with zeros
        df['Holiday Charge'] = 0
        df['Weekend Charge'] = 0

        # Define the holidays (you can specify the country)
        us_holidays = holidays.UnitedStates(years=df['Pickup Date'].dt.year.unique())

        # Update 'Holiday Charge' and 'Weekend Charge' based on conditions
        for index, row in df.iterrows():
            pickup_date = row['Pickup Date']
            
            # Check if the date is a holiday
            if pickup_date in us_holidays:
                df.at[index, 'Holiday Charge'] = 50
            
            # Check if the date is a weekend (Saturday=5, Sunday=6)
            if pickup_date.weekday() in [5, 6]:
                df.at[index, 'Weekend Charge'] = 25

        df['Pickup Time'] = pd.to_datetime(df['Pickup Time'], format='%H:%M:%S')

        # Initialize 'After Hours' column with zeros
        df['AfterHours Charge'] = 0

        # Define the time thresholds
        morning_threshold = pd.to_datetime('08:00:00', format='%H:%M:%S').time()
        evening_threshold = pd.to_datetime('20:00:00', format='%H:%M:%S').time()

        # Update 'After Hours' based on the condition
        for index, row in df.iterrows():
            pickup_time = row['Pickup Time'].time()
            
            if pickup_time < morning_threshold or pickup_time >= evening_threshold:
                df.at[index, 'AfterHours Charge'] = 15



        df['total_sum'] = df["Weight Charge"] + df['Vehicle Charge'] + df['DG fee'] + df['Pieces Charge'] + df['Toll charge'] + df['Overnight Hold Charge']  + df['Non-Contiguous'] + df['GPS Fee'] + df['Airline Transfer Charge'] +df['Holiday Charge'] +df['Weekend Charge'] + df['AfterHours Charge'] 
        df['Fuel Surcharge'] = df['total_sum']* df['FS percetage']
        df['Security Surcharge'] = df['total_sum']* .065


        # add attempt, Wait time
        df['Final Quote'] = df["Weight Charge"] + df['Vehicle Charge'] + df['DG fee'] + df['Pieces Charge'] + df['Toll charge'] + df['Overnight Hold Charge']  + df['Non-Contiguous'] + df['GPS Fee'] + df['Airline Transfer Charge'] + df['Fuel Surcharge'] + df['Security Surcharge']+df['Holiday Charge'] +df['Weekend Charge'] + df['AfterHours Charge'] 
        final_quote = df['Final Quote'].iloc[0] 
    
    # Update the quote in the placeholder
    quote_placeholder.markdown(
        f'<div style="background-color: #001f3f; padding: 10px; border-radius: 10px; text-align: center;">'
        f'<p style="color: white; font-size: 18px;">Quote: ${final_quote:.2f}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.write(f"Pickup -  Mileage: {pickup_mileage:.1f} miles - Toll: {pickup_estimated_toll} $")
    st.write(f"Delivery - Mileage : {del_mileage:.1f} miles - Toll: {del_estimated_toll} $ ")

    st.header("Billing Charges")

    if df['Weight Charge'].iloc[0] != 0:
        st.write(f"Weight Charge - {df['Weight Charge'].iloc[0]:.2f} $ ")

    if df['Vehicle Charge'].iloc[0] != 0:
        st.write(f"Vehicle Charge - {df['Vehicle Charge'].iloc[0]:.2f} $ ")

    if df['Pieces Charge'].iloc[0] != 0:
        st.write(f"Pieces Charge -  {df['Pieces Charge'].iloc[0]:.2f} $ ")

    if df['DG fee'].iloc[0] != 0:
        st.write(f"DG Fee - {df['DG fee'].iloc[0]:.2f} $ ")

    if df['Toll charge'].iloc[0] != 0:
        st.write(f"Toll Fee - {df['Toll charge'].iloc[0]:.2f} $ ")

    if df['Non-Contiguous'].iloc[0] != 0:
        st.write(f"HI-AL Fee - {df['Non-Contiguous'].iloc[0]:.2f} $ ")

    if df['Airline Transfer Charge'].iloc[0] != 0:
        st.write(f"Airline Transfer Fee - {df['Airline Transfer Charge'].iloc[0]:.2f} $ ")

    if df['Overnight Hold Charge'].iloc[0] != 0:
        st.write(f"Overnight Hold Fee - {df['Overnight Hold Charge'].iloc[0]:.2f} $ ")

    if df['GPS Fee'].iloc[0] != 0:
        st.write(f"GPS Fee - {df['GPS Fee'].iloc[0]:.2f} $ ")

    if df['Holiday Charge'].iloc[0] != 0:
        st.write(f"Holiday Fee - {df['Holiday Charge'].iloc[0]:.2f} $ ")

    if df['Weekend Charge'].iloc[0] != 0:
        st.write(f"Weekend Fee - {df['Weekend Charge'].iloc[0]:.2f} $ ")

    if df['AfterHours Charge'].iloc[0] != 0:
        st.write(f"AfterHour Fee - {df['AfterHours Charge'].iloc[0]:.2f} $ ")

    if df['Security Surcharge'].iloc[0] != 0:
        st.write(f"Security Surcharge - {df['Security Surcharge'].iloc[0]:.2f} $ ")

    if df['Fuel Surcharge'].iloc[0] != 0:
        st.write(f"Fuel Surcharge - {df['Fuel Surcharge'].iloc[0]:.2f} $ ")



    # st.write(df)






# Map of Pickup and Delivery
# st.header("Map of Pickup and Delivery")

# # Create a PyDeck scatterplot map
# pickup_location = {"JFK": (40.6413, -73.7781), "LAX": (33.9416, -118.4085), "ORD": (41.9742, -87.9073),
#                    "ATL": (33.6367, -84.4277), "DFW": (32.8975, -97.0404)}


# if pickup_airport in pickup_location and delivery_airport in pickup_location:
#     map_center = ((pickup_location[pickup_airport][0] + pickup_location[delivery_airport][0]) / 2,
#                   (pickup_location[pickup_airport][1] + pickup_location[delivery_airport][1]) / 2)

#     map_data = [
#         {
#             "pickup_airport": pickup_airport,
#             "delivery_airport": delivery_airport,
#             "lat": map_center[0],
#             "lon": map_center[1],
#         }
#     ]

#     df = pd.DataFrame(map_data)

#     # Create a line layer to connect the two airports with a red line
#     line_layer = pdk.Layer(
#         "LineLayer",
#         data=df,
#         get_source="[lon, lat]",
#         get_target="[lon, lat]",
#         get_color=[255, 0, 0],
#         get_width=5,
#     )

#     st.pydeck_chart(
#         pdk.Deck(
#             map_style="mapbox://styles/mapbox/dark-v9",
#             initial_view_state=pdk.ViewState(
#                 latitude=map_center[0],
#                 longitude=map_center[1],
#                 zoom=5,
#                 pitch=0,
#             ),
#             layers=[line_layer],
#         ))
 
# Hide the "Made with Streamlit" tag
st.markdown("<style>div[data-testid='stFooter']>div{display:none}</style>", unsafe_allow_html=True)
