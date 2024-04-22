import { CameraPreview } from '../components/Camera';
import React, { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, useWindowDimensions } from 'react-native';
import { Image } from 'expo-image';
import { manipulateAsync, FlipType, SaveFormat } from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';
import { BoardRenderer } from '../components/BoardRenderer';

const BoardReader = () => {
    const [solution, setSolution] = useState(null);
    const [board, setBoard] = useState(null);
    const [picture, setPicture] = useState(null);
    const { height, width } = useWindowDimensions();
    const [currentGoal, setGoal] = useState(null);

    const onTakePicture = async () => {
        setPicture(null);
        setGoal(null);
        setSolution(null);
        setBoard(null);
    }

    const onPictureSaved = async (picture) => {
        try {
            setPicture(picture);
            const response = await FileSystem.uploadAsync('http://192.168.0.16:5000/read', picture.uri, {
                httpMethod: 'POST',
                uploadType: FileSystem.FileSystemUploadType.MULTIPART,
                fieldName: 'file'
            });
            const data = JSON.parse(response.body);
            setBoard(data.board);
        }
        catch (error) {
            console.error(error);
        }
    };

    const solve = async () => {
        const colors = {
            "r": "red",
            "g": "green",
            "b": "blue",
            "y": "yellow",
            "m": "red"
        }
        const response = await fetch('http://192.168.0.16:5000/solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                board: board,
                goal: board["goals"][currentGoal],
                robot: colors[currentGoal[0]],
            }),
        });
        const data = await response.json();
        const { uri } = await FileSystem.downloadAsync('http://192.168.135.165:5000/solution/' + data.solution_id, FileSystem.documentDirectory + 'solution.gif');
        setSolution({ uri: uri });

    };

    const getStatus = () => {
        if (picture && !board) {
            return (<Text>{"Analyzing"}</Text>);
        } else if (board && !currentGoal) {
            return (<Text>{"Select a goal"}</Text>);
        } else if (board && currentGoal && !solution) {
            return (<Button title={"Solve"} onPress={solve}></Button>);
        }
        else {
            return (<View></View>);
        }
    }
    return (
        <View style={styles.container}>
            <CameraPreview onTakePicture={onTakePicture} onPictureSaved={onPictureSaved} />
            <View style={styles.status}>{getStatus()}</View>
            <View style={styles.solutionContainer}>
                {!solution && board && (<BoardRenderer board={board} currentGoal={currentGoal} setGoal={setGoal} />)}
                {!board && picture && (<Image style={styles.solution} source={picture} contentFit={"contain"}></Image>)}
                {solution && (<Image style={styles.solution} source={solution} contentFit={"contain"}></Image>)}
            </View>

        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'space-between',
        ...StyleSheet.absoluteFill,
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
    text: {
        fontSize: 24,
        color: 'white',
    },
    cropBox: {
        width: '80%',
        borderWidth: 2,
        borderColor: 'red',
    },
    solutionContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    solution: {
        flex: 1,
        width: '80%',
        height: '100%',
        resizeMode: 'contain',
    },
    status: {
        justifyContent: 'center',
        alignItems: 'center',
        height: 40,
        width: '100%',
    },
});

export { BoardReader };