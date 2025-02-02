import cv2
import pandas as pd
import time
import numpy as np
import statsmodels.api as sm
from subprocess import call
import matplotlib.pyplot as plt
import argparse


# Initialize the list to store coordinates and timestamps
data = []

# Function to track the laser
def lin_interporlate(start_point, end_point, num_points):
    delta_time = (end_point[0] - start_point[0])/(num_points)
    delta_x = (end_point[1] - start_point[1])/num_points
    delta_y = (end_point[2] - start_point[2])/num_points
    faux_z = 0.02

    for i in range(1,num_points):
        tmp_time = start_point[0] + delta_time * i 
        tmp_x = start_point[1] + delta_x * i
        tmp_y = start_point[2] + delta_y * i
        data.append([tmp_time, tmp_x, tmp_y, faux_z])

    return

def track_laser(video_path, output_csv, num_points_interp):
    global data
    # Open the video
    cap = cv2.VideoCapture(video_path)
    faux_z = 0.02
    first_measure = True
    
    # Check if video opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        return

    # Read until video is completed
    count = 0
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            # Convert to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define range of pink color in HSV
            lower_pink = (150, 50, 50)
            upper_pink = (165, 255, 255)
            # Threshold the HSV image to get only pink colors
            mask = cv2.inRange(hsv, lower_pink, upper_pink)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest contour assuming it's the laser
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    scaling_factor = 0.16  # Adjust this scaling factor as needed
                    printed_cX = int(M["m10"] / M["m00"])
                    printed_cY = int(M["m01"] / M["m00"])
                    cX = int(M["m10"] / M["m00"] * scaling_factor)
                    cY = int(M["m01"] / M["m00"] * scaling_factor)
                    # Save the timestamp and coordinates
                    curr_time = round(time.time() * 1000)
                    if first_measure: 
                        time_ref = round(time.time() * 1000)
                        time_elapsed = (curr_time - time_ref) / 1000
                        first_measure = False
                    else:
                        time_elapsed = (curr_time - time_ref) / 1000
                        lin_interporlate(data[-1], [time_elapsed, cX, cY, faux_z], num_points_interp)

                    cv2.circle(frame, (printed_cX, printed_cY), 5, (255, 0, 0), -1)

                    data.append([time_elapsed, cX, cY, faux_z])
                    count += 1
                    
                    # Optionally, visualize the tracking
                    
                else:
                    print("No laser detected.")
            
            # Display the frame
            cv2.imshow('Frame', frame)
            
            # Press Q on keyboard to exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()

    # Applying LOWESS smoothing to the data
    df = pd.DataFrame(data, columns=['Time', 'X', 'Y', 'Faux_Z'])
    frac = 0.1  # Fraction of data points to use in each local regression
    df['X_smoothed'] = sm.nonparametric.lowess(df['X'], df['Time'], frac=frac, return_sorted=False)
    df['Y_smoothed'] = sm.nonparametric.lowess(df['Y'], df['Time'], frac=frac, return_sorted=False)

    # Save the smoothed data to a CSV file
    df[['Time','X_smoothed', 'Y_smoothed', 'Faux_Z']].to_csv(output_csv, index=False, header=None)
    print(f"Smoothed data saved to {output_csv}")
    graph(df['X_smoothed'],df['Y_smoothed'])

def graph(x_values,y_values):
    # Plot scatter points
    plt.scatter(x_values, y_values, color='blue', alpha=0.5)

# Sort data by x-values
    plt.plot(x_values, y_values, linestyle='-', color='red')

# Add labels and title
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.title('Scatter Plot of Points with Lines')

# Show grid
    plt.grid(True)

# Show the plot
    plt.show()
    

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Process data and plot smoothed curves.')

    # Add arguments
    parser.add_argument('input_video', type=str, help='Input MP4 file containing data')
    parser.add_argument('-o','--output', type=str, default='laser_coordinates.csv', help='Output file to save the waypoints (default: laser_coordinates.csv)')
    parser.add_argument('-i','--interpt', type=int, default=2, help='Number of points to linearly interporlate')
    parser.add_argument('-f','--frac', type=float, default=0.1, help='Fraction of data used for smoothing')

    # Parse arguments
    args = parser.parse_args()

    track_laser(args.input_video, args.output, args.interpt) 

    # print("Generate IKs...")
    # with open('gen_ik.sh', 'rb') as file:
    #      script = file.read()
    # rc = call(script, shell=True)
    # print("IKs Generated")
