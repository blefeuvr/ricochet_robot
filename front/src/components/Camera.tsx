import { Camera, CameraType, takePictureAsync } from 'expo-camera';
import React, { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, useWindowDimensions } from 'react-native';
import { Image } from 'expo-image';
import { manipulateAsync, FlipType, SaveFormat } from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';

const CameraPreview = ({ onTakePicture, onPictureSaved }) => {
    const [permission, requestPermission] = Camera.useCameraPermissions();
    const [camera, setCamera] = useState(null);
    const [cameraReady, setCameraReady] = useState(false);
    const { height, width } = useWindowDimensions();

    if (!permission) return <View />;

    if (!permission.granted) {
        return (
            <View style={[styles.placeHolder, { width: width, height: width }]}>
                <Text>No access to camera</Text>
                <Button title="Request Permissions" onPress={requestPermission} />
            </View>
        );
    }

    async function takePicture() {
        onTakePicture();
        console.log("Taking picture")
        if (camera) {
            const rawPicture = await camera.takePictureAsync();
            const croppedPicture = await manipulateAsync(
                rawPicture.uri,
                [{
                    crop: {
                        originX: Math.floor(rawPicture.width * 0.1),
                        originY: Math.floor(rawPicture.height * 0.1),
                        height: Math.floor(rawPicture.height * 0.8),
                        width: Math.floor(rawPicture.width * 0.8)
                    }
                }],
                { format: SaveFormat.PNG }
            );
            onPictureSaved(croppedPicture);
        }
    }

    return (
        <Camera style={[styles.camera, { width: width, height: width }]} type={CameraType.back} ref={(ref) => { setCamera(ref) }} ratio={"1:1"} onCameraReady={() => setCameraReady(true)}>
            <TouchableOpacity style={styles.button} onPress={takePicture}>
                <View style={styles.placeHolder}></View>
                <View style={[styles.cropBox, { height: width * 0.8 }]}></View>
                <View style={styles.placeHolder}>
                    <Text style={styles.text}>Click to scan</Text>
                </View>
            </TouchableOpacity>
        </Camera>
    );
};

const styles = StyleSheet.create({
    placeHolder: {
        justifyContent: 'center',
        alignItems: 'center',
    },
    camera: {
    },
    button: {
        justifyContent: 'space-around',
        alignItems: 'center',
        flex: 1,
        ...StyleSheet.absoluteFill,
    },
    cropBox: {
        width: '80%',
        borderWidth: 2,
        borderColor: 'red',
    },
    placeHolder: {
        height: '10%',
        justifyContent: 'center',
        alignItems: 'center',
    },
    text: {
        color: 'red',
    }
});

export { CameraPreview };