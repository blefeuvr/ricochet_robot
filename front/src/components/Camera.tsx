import { CameraView, CameraType, useCameraPermissions } from "expo-camera";
import React, { useState, useEffect } from "react";
import {
  Button,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  useWindowDimensions,
} from "react-native";
import { Image } from "expo-image";
import { manipulateAsync, FlipType, SaveFormat } from "expo-image-manipulator";
import * as FileSystem from "expo-file-system";

const CameraPreview = ({ onTakePicture, onPictureSaved }) => {
  const [permission, requestPermission] = useCameraPermissions();
  const [camera, setCamera] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [pictureSize, setPictureSize] = useState(null);
  const { height, width } = useWindowDimensions();

  useEffect(() => {
    const getPictureSize = async () => {
      const pictureSizes = await camera.getAvailablePictureSizesAsync();
      const squareSizes = pictureSizes
        .filter((size) => {
          const [width, height] = size.split("x");
          return width == height;
        })
        .sort();
      setPictureSize(squareSizes[squareSizes.length - 1]);
    };
    if (camera) {
        getPictureSize();
    }
  }, [camera]);

  async function takePicture() {
    onTakePicture();
    console.log("Taking picture");
    if (camera) {
      const rawPicture = await camera.takePictureAsync();
      const croppedPicture = await manipulateAsync(
        rawPicture.uri,
        [
          {
            crop: {
              originX: Math.floor(rawPicture.width * 0.1),
              originY: Math.floor(rawPicture.width * 0.1),
              height: Math.floor(rawPicture.width * 0.8),
              width: Math.floor(rawPicture.width * 0.8),
            },
          },
        ],
        { format: SaveFormat.PNG }
      );
      onPictureSaved(croppedPicture);
    }
  }

  if (!permission) return <View />;

  if (!permission.granted) {
    return (
      <View style={[styles.placeHolder, { width: width, height: width }]}>
        <Text>No access to camera</Text>
        <Button title="Request Permissions" onPress={requestPermission} />
      </View>
    );
  }

  return (
    <View
      style={[
        {
          flex: 1,
          width: width,
          height: width,
          //   overflow: "hidden",
        },
      ]}
    >
      <CameraView
        style={[
          {
            // flex: 1,
            width: width,
            height: width,
          },
        ]}
        facing={"back"}
        ref={(ref) => {
          setCamera(ref);
        }}
        onCameraReady={() => setCameraReady(true)}
        pictureSize={pictureSize}
        zoom={0}
        // animateShutter={false}
      ></CameraView>
      <TouchableOpacity
        style={[
          {
            position: "absolute",
            width: width,
            height: width,
            alignItems: "center",
          },
        ]}
        onPress={takePicture}
      >
        <View style={styles.placeHolder}></View>
        <View style={[styles.cropBox, { height: width * 0.8 }]}></View>
        <View style={styles.placeHolder}>
          <Text style={styles.text}>Click to scan</Text>
        </View>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  placeHolder: {
    justifyContent: "center",
    alignItems: "center",
  },
  camera: {},
  button: {
    justifyContent: "space-around",
    alignItems: "center",
    flex: 1,
    ...StyleSheet.absoluteFill,
  },
  cropBox: {
    width: "80%",
    borderWidth: 2,
    borderColor: "red",
  },
  placeHolder: {
    height: "10%",
    justifyContent: "center",
    alignItems: "center",
  },
  text: {
    color: "red",
  },
});

export { CameraPreview };
