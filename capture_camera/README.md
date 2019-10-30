## Auto save image form hikvison web camera or usb camera 

### run
You only need to configure the `cfg.yaml` file, then run
```bash
python camera.py
```
Images of all cameras will be saved at the same time, and it will create folder of `image` to save all images.

### configuration
#### Note
There need a symbol of `-` in the front of every configuration of one camera.

#### general
```
autosave:  Whether auto save image, if it is true, images of all cameras will be saved at the same time with a rate of fps; if it is false, images will be saved when you press the Enter key.
fps:  Auto save rate, integer
```
 
#### cameras
```
enable:  Whether use this camera
type:  web_camera, usb_camera
user:  user name， only for hikvision web camera
passwd:  password, only for hikvision web camera
ip:  ip, only for hikvision web camera
port: usb port, only for usb camera
undistort: undistort image before save image
    enable:  Whether undistort image
    distortion_parameters: Distortion parameter, k1, k2
    image_size: Row and column
    intrinsic_parameters: Camera parameter, fx, fy, cx, cy
    retain_black_edge: 0-1, 1- retain black edge, 0- do not retain black edge
resize: Resize image
    enable: Whether resize image
    image_size: New size
```


