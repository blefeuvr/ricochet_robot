import { Camera, CameraType, takePictureAsync } from 'expo-camera';
import React, { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, useWindowDimensions, Image } from 'react-native';
import { manipulateAsync, FlipType, SaveFormat } from 'expo-image-manipulator';

const Solution = () => {
    const [image, setImage] = useState(null);
    const [camera, setCamera] = useState(null);
    const [cameraReady, setCameraReady] = useState(false);
    const [permission, requestPermission] = Camera.useCameraPermissions();
    const { height, width } = useWindowDimensions();

    if (!permission) return <View />;

    if (!permission.granted) {
        return (
            <View style={styles.container}>
                <Text>No access to camera</Text>
                <Button title="Request Permissions" onPress={requestPermission} />
            </View>
        );
    }

    async function takePicture() {
        if (camera) {
            const picture = await camera.takePictureAsync({ onPictureSaved: this.onPictureSaved });
            console.log(picture);
            const manipResult = await manipulateAsync(
                picture.uri,
                [{
                    crop: {
                        originX: Math.floor(picture.width * 0.1),
                        originY: Math.floor(picture.height * 0.1),
                        height: Math.floor(picture.height * 0.8),
                        width: Math.floor(picture.width * 0.8)
                    }
                }],
                { compress: 1, format: SaveFormat.PNG }
            );
            console.log(manipResult);
            setImage(manipResult);
        }
    }
    return (
        <View style={styles.container}>
            <Camera style={[styles.camera, {width: width, height: width}]} type={CameraType.back} ref={(ref) => {setCamera(ref)}} ratio={"1:1"} onCameraReady={() => setCameraReady(true)}>
                <View style={[styles.cropBox, { height: width * 0.8 }]}></View>
            </Camera>
            <View style={[styles.interface, StyleSheet.absoluteFill]}>
                <View style={styles.buttonContainer}>
                    {image && (<Image style={styles.tinyPreview} source={image}></Image>)}
                    <TouchableOpacity style={styles.button} onPress={takePicture}>
                        <Text style={styles.text}>Read board</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
    },
    camera: {
        justifyContent: 'center',
        alignItems: 'center',
    },
    interface: {
        position: 'absolute',
        flex: 1,
        borderWidth: 2,
        borderColor: 'black'
    },
    buttonContainer: {
        flex: 1,
        flexDirection: 'row',
        backgroundColor: 'transparent',
        margin: 64,
    },
    button: {
        flex: 1,
        alignSelf: 'flex-end',
        alignItems: 'center',
        backgroundColor: 'black',
    },
    text: {
        fontSize: 24,
        color: 'white',
    },
    cropBox: {
        width: '80%',
        borderWidth: 2,
        borderColor: 'red',
    },
    tinyPreview: {
        width: 50,
        height: 50,
    }
});

export { Solution };