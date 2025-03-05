import cv2
import matplotlib.pyplot as plt
import requests
import configparser

# Replace 'your url here' with the URL provided by your phone's app
video_url = 'your url here' # example: http://198.158.8.6:8880/video (This is a fake url)

def phone_camera(video_url):    
    cap = cv2.VideoCapture(video_url)  # Open the video feed

    while True:
        ret, frame = cap.read()  # Read the frame
        if not ret:  # If frame is not read, break the loop
            print("Failed to grab frame")
            break

        cv2.imshow('Phone Camera Feed', frame)  # Display the frame
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # If 'q' is pressed, break the loop
            break
        
    cap.release()
    cv2.destroyAllWindows()

def phone_camera_with_save(video_url):    
    cap = cv2.VideoCapture(video_url)  # Open the video feed

    while True:
        ret, frame = cap.read()  # Read the frame
        if not ret:  # If frame is not read, break the loop
            print("Failed to grab frame")
            break

        cv2.imshow('Phone Camera Feed', frame)  # Display the frame
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # If 'q' is pressed, break the loop
            break
        if cv2.waitKey(1) & 0xFF == ord('s'):  # If 's' is pressed, save the frame
            cv2.imwrite('frame.jpg', frame)  # Save the frame as 'frame.jpg'
            
            # Display the saved frame
            plt.imshow(frame)
            plt.axis('off')
            plt.show()

            break

    cap.release()
    cv2.destroyAllWindows()

def phone_camera_with_rotate_save(video_url):    
    cap = cv2.VideoCapture(video_url)  # Open the video feed

    # Increase the resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    while True:
        ret, frame = cap.read()  # Read the frame
        if not ret:  # If frame is not read, break the loop
            print("Failed to grab frame")
            break

        cv2.namedWindow('Phone Camera Feed', cv2.WINDOW_NORMAL)  # Create a resizable window
        cv2.resizeWindow('Phone Camera Feed', 320, 480)  # Resize the window to 320x480

        # Rotate the video display
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  # Rotate the frame 90 degrees clockwise
        cv2.imshow('Phone Camera Feed', frame)  # Display the frame
                
        if cv2.waitKey(1) & 0xFF == ord('q'):  # If 'q' is pressed, break the loop
            break
        if cv2.waitKey(1) & 0xFF == ord('s'):  # If 's' is pressed, save the frame
            cv2.imwrite('slip_image.jpg', frame)  # Save the frame as 'slip_image.jpg'
                                 
            # Display the saved frame
            plt.imshow(frame)
            plt.axis('off')
            plt.show()

            break

    cap.release()
    cv2.destroyAllWindows()

def extract_text_from_image(api_key):
    api_url = 'https://api.api-ninjas.com/v1/imagetotext'
    with open('slip_image.jpg', 'rb') as image_file_descriptor:
        files = {'image': image_file_descriptor}
        r = requests.post(api_url, files=files, headers={'X-Api-Key': api_key})
        # Extract the text from the JSON result
        text_list = [item['text'] for item in r.json()]
        extracted_text = ' '.join(text_list)
        print(extracted_text)
        return extracted_text

# Main code
if __name__ == "__main__":
    # Read the API key from the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key_text = config['API']['your_api_key']
    
    # Capture and process the video
    phone_camera_with_rotate_save(video_url)
    
    # Extract text from the saved image
    extracted_text = extract_text_from_image(api_key_text)
