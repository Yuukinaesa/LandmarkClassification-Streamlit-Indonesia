import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static

# Define the class names
nama_class = ['Candi Borobudur', 'Gedung Sate', 'Istana Maimun', 'Jembatan Ampera', 'Monumen Nasional']

# Define the locations of each class
class_locations = {
    'Candi Borobudur': {'name': 'Candi Borobudur', 'Latitude': -7.60788, 'Longitude': 110.20367, 'city' : 'Magelang',
                        'desc': 'Candi Borobudur is a 9th-century Mahayana Buddhist temple located in Central Java, Indonesia. This massive temple is one of the greatest Buddhist monuments in the world and has become a popular tourist destination. The temple features 2,672 relief panels and 504 Buddha statues, with the main dome at the center of the top platform surrounded by 72 Buddha statues seated inside perforated stupa. It was declared a UNESCO World Heritage Site in 1991.'},
	'Gedung Sate': {'name': 'Gedung Sate', 'Latitude': -6.90249, 'Longitude': 107.61872, 'city' : 'Bandung',
                    'desc': 'Gedung Sate is a government building located in Bandung, West Java, Indonesia. The building was built in 1920 and served as the regional headquarters of the Dutch East Indies government. The building features a unique style of architecture that blends Dutch and traditional Sundanese elements. The building is named after the satay skewers that are sold by vendors nearby. Today, the building is used as the office of the Governor of West Java and is a popular landmark and tourist attraction.'},
	'Istana Maimun': {'name': 'Istana Maimun', 'Latitude': 3.5752, 'Longitude': 98.6837, 'city' : 'Medan',
                      'desc': 'Istana Maimun is a palace of the Sultanate of Deli located in Medan, North Sumatra, Indonesia. The palace was built in 1888 and features a unique blend of Malay, Islamic, and European styles of architecture. The palace is open to the public and visitors can explore the various rooms and galleries that display the history and culture of the sultanate. The palace also houses a collection of royal regalia, including the throne, crown, and royal carriage.'},
    'Jembatan Ampera': {'name': 'Jembatan Ampera', 'Latitude': -2.99178, 'Longitude': 104.76354, 'city' : 'Palembang',
                        'desc': 'Jembatan Ampera is a vertical-lift bridge located in Palembang, South Sumatra, Indonesia. The bridge spans across the Musi River and was built in 1965. The bridge has become a symbol of the city and is an important transportation link between the northern and southern parts of Palembang. The bridge is also a popular spot for tourists to enjoy the view of the Musi River and the city skyline.'},
	'Monumen Nasional': {'name': 'Monumen Nasional', 'Latitude': -6.1754, 'Longitude': 106.8272, 'city' : 'Jakarta',
                         'desc': 'Monumen Nasional is a monument located in the center of Merdeka Square, Central Jakarta, Indonesia. The monument was built in 1961 to commemorate the struggle for Indonesian independence. The monument stands at a height of 132 meters and is topped by a flame covered in gold foil. Visitors can take an elevator to the top of the monument and enjoy a panoramic view of Jakarta. The monument is surrounded by a park and various museums that showcase the history and culture of Indonesia.'},
}



# Load the model
model = load_model('model.h5')

# Function to preprocess the image
def preprocess_image(image):
    img = image.resize((224, 224))
    img = np.array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# Define the prediction function
def predict(image):
    try:
        # Preprocess the image
        img = preprocess_image(image)
        # Predict the class probabilities
        probabilities = model.predict(img)[0]
        # Get the predicted class index
        predicted_class_idx = np.argmax(probabilities)
        # Get the predicted class name
        predicted_class = nama_class[predicted_class_idx]
        # Get the probability of the predicted class
        predicted_prob = probabilities[predicted_class_idx]
        # Convert the probability to a percentage
        predicted_prob_pct = round(predicted_prob * 100, 2)
        # Convert the probabilities to percentages
        probabilities_pct = [round(prob * 100, 2) for prob in probabilities]
        # Return the predicted class name and probabilities
        return (predicted_class, predicted_prob_pct, probabilities_pct)
    except:
        # Return None if the image cannot be processed
        return None

# Set up the Streamlit app
st.set_page_config(page_title="Image Classification", page_icon=":🏛️:")
st.title("Klasifikasi Landmark")
st.write("Unggah gambar dan aplikasi akan mengklasifikasikannya ke dalam salah satu kelas berikut:")
st.write(nama_class)


# Add a map to the app
geolocator = Nominatim(user_agent="Landmark", timeout=10)
location = geolocator.geocode("Indonesia") # Initial location
m = folium.Map(location=[location.latitude, location.longitude], zoom_start=5)


# Add a file uploader to the app
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image
    image = Image.open(uploaded_file)
    # Show the image
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    # Make a prediction
    prediction = predict(image)
    if prediction is not None:
        predicted_class, predicted_prob, probabilities = prediction
        # Show the predicted class and probability
        st.write("Predicted class:", predicted_class)
        st.write("Probability:", predicted_prob, "%")
        # Show the probabilities for each class
        for class_name, prob in zip(nama_class, probabilities):
            st.write(class_name, ":", prob, "%")
        # Get the location of the predicted class
        class_location = class_locations[predicted_class]
        # Add a marker to the map
        folium.Marker(
            location=[class_location['Latitude'], class_location['Longitude']],
            popup=class_location['name'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        # Zoom to the location
        m.fit_bounds([[class_location['Latitude'], class_location['Longitude']]])
		# Show the class location

        st.write("Address:", class_location)

        # Update the map
        folium_static(m, width=700, height=500)
