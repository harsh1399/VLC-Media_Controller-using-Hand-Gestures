# VLC-Media_Controller-using-Hand-Gestures

The idea of the project is to control VLC media players functionalities such as pause/play, volume increase/decrease using hand gesture detected using object detection mechanisms.
I used MediaPipe (object detection library) hand and finger tracking solution. 

[MediaPipe Library](https://google.github.io/mediapipe/solutions/hands.html)

## How to use?
Create a virtual environment and install all the requirements - 
```
pip install -r requirements.txt
```
At line 12 in HandGesture.py, add the filename you want to play in VLC media player.
```
media = vlc.MediaPlayer(FILENAME)
```
Execute the file.
