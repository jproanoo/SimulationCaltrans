import folium 
import pandas as pd
import xlrd
import requests
import subprocess
import xml.etree.ElementTree as ET


class Traffic:
    def __init__(self,path):
        self.path=path
        
    def leerFile(self,sheet):
        xls = pd.ExcelFile(self.path)
        df = pd.read_excel(xls, sheet)
        return df
    

    def GraphPoints(self,data,name):
        map = folium.Map(location=[data['Lat'].mean(), data['Long'].mean()], zoom_start=5)

        # Add markers to the map for each coordinate
        for index, row in data.iterrows():
            folium.Marker([row['Lat'], row['Long']], popup=row['Name']).add_to(map)

        # Display the map
        map.save(name+".html")  # Save the map to an HTML file
        return map
    def downloadMapOSM(self,data,name):
        min_lat, max_lat = data['Lat'].min(), data['Lat'].max()
        min_lon, max_lon = data['Long'].min(), data['Long'].max()

        # Define the bounding box based on the minimum and maximum coordinates
        bbox = (min_lat, min_lon, max_lat, max_lon)

        # Define the Overpass query to retrieve map data within the bounding box
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
            [out:xml];
            (
                node({bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]});
                way({bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]});
                relation({bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]});
            );
            out meta;
            """

# Send a POST request to the Overpass API with the query
        response = requests.post(overpass_url, data=overpass_query)

# Save the response content (the .osm file)
        with open(name+".osm", "wb") as file:
            file.write(response.content)

        print("Map downloaded successfully as map.osm")
        
    def convert_osm_to_sumo(self, output_file):
        """
        Convert OSM file to SUMO network format using netconvert tool.
    
        Parameters:
        osm_file (str): Path to the input OSM file.
        output_file (str): Path to the output SUMO network file.
        """
        try:
        # Construct the netconvert command
            netconvert_cmd = ["netconvert", "--osm-files", "mapa1.osm,mapa2.osm,mapa3.osm", "-o", output_file,"--keep-edges.by-type","highway.motorway,highway.motorway_link,highway.trunk,highway.trunk_link,highway.primary,highway.primary_link"]
        
        # Run netconvert as a subprocess
            subprocess.run(netconvert_cmd, check=True)
        
            print("Conversion successful.")
        except subprocess.CalledProcessError as e:
            print(f"Conversion failed: {e}")

    import subprocess

def generate_random_routes(net_file, route_file, num_routes, seed):
    # Command to generate random routes using randomTrips.py
    command = [
        "/usr/share/sumo/tools/randomTrips.py",
        "-n", net_file,
        "-r", route_file,
        "-e", str(num_routes),
        "--seed", str(seed)
    ]
    
    # Execute the command
    try:
        subprocess.run(command, check=True)
        print("Random routes generated successfully!")
    except subprocess.CalledProcessError as e:
        print("Error generating random routes:", e)


    
       
if __name__=="__main__":
    path="2000_sec_2023_12_listo.xls"
    trafico=Traffic(path)
    sheet="Stations"
    coordenadas=trafico.leerFile(sheet)
    coordenadasforPlot=coordenadas[['Lat', 'Long','ID','Name','Lanes']]
    selectedCoordenadas1=coordenadasforPlot[0:4]
    selectedCoordenadas2=coordenadasforPlot[3:8]
    selectedCoordenadas3=coordenadasforPlot[7:12]
    selectedCoordenadas4=coordenadasforPlot[11:16]
    
    mapa1=trafico.GraphPoints(coordenadasforPlot[0:16],"mapa1")
    
    trafico.downloadMapOSM(selectedCoordenadas1,"mapa1")
    trafico.downloadMapOSM(selectedCoordenadas2,"mapa2")
    trafico.downloadMapOSM(selectedCoordenadas3,"mapa3")
    trafico.downloadMapOSM(selectedCoordenadas4,"mapa4")
    trafico.convert_osm_to_sumo('net.net.xml')
    
    net_file = "net.net.xml"
    
    # Output file for the generated routes
    route_file = "random_routes.rou.xml"
    
    # Number of random routes to generate
    num_routes = 300
    
    # Seed for random number generation (optional)
    seed = 123
    
    # Generate random routes
    generate_random_routes(net_file, route_file, num_routes, seed)