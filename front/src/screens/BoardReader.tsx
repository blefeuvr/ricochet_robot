import { CameraPreview } from '../components/Camera';
import React, { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, useWindowDimensions } from 'react-native';
import { Image } from 'expo-image';
import { manipulateAsync, FlipType, SaveFormat } from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';
import { BoardRenderer } from '../components/BoardRenderer';

const BoardReader = () => {
    const [solution, setSolution] = useState(null);
    const [error, setError] = useState(null);
    const [board, setBoard] = useState(null);
    const [picture, setPicture] = useState(null);
    const [currentGoal, setGoal] = useState(null);
    const [status, setStatus] = useState("start");
    const { height, width } = useWindowDimensions();

    const onTakePicture = async () => {
        setPicture(null);
        setGoal(null);
        setSolution(null);
        setBoard(null);
        setError(null);
        setStatus("analyzing");
    }

    const onPictureSaved = async (picture) => {
        try {
            setPicture(picture);
            const response = await FileSystem.uploadAsync('https://blefeuvr.fr:5000/read', picture.uri, {
                httpMethod: 'POST',
                uploadType: FileSystem.FileSystemUploadType.MULTIPART,
                fieldName: 'file'
            });
            const data = JSON.parse(response.body);
            if (data.msg == "error") {
                setError(data.error);
                setStatus("error");
            } else {
                setStatus("waitingGoal");
                setBoard(data.board);
            }
        }
        catch (error) {
            console.error(error);
        }
    };

    const solve = async () => {
        setStatus("solving");
        const colors = {
            "r": "red",
            "g": "green",
            "b": "blue",
            "y": "yellow",
            "m": "red"
        }
        const response = await fetch('https://blefeuvr.fr:5000/solve', {
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
        setBoard(data.board);
        console.log(data.board["robots"]);
        setSolution(data.moves);
        setStatus("done");
    };

    const getStatus = () => {
        if (status == "start") {
            return (<View></View>);
        } else if (status == "analyzing") {
            return (<Text>{"Analyzing..."}</Text>);
        } else if (status == "error") {
            return (<Text>{"Failed to analyze, please take again"}</Text>);
        } else if (status == "waitingGoal" && !currentGoal) {
            return (<Text>{"Select a goal"}</Text>);
        } else if (status == "waitingGoal") {
            return (<Button title={"Solve"} onPress={solve}></Button>);
        } else if (status == "solving") {
            return (<Text>{"Solving..."}</Text>);
        } else if (status == "done") {
            return (<Text>{`Done in ${solution.length} moves`}</Text>);
        }
    }

    return (
        <View style={styles.container}>
            <CameraPreview onTakePicture={onTakePicture} onPictureSaved={onPictureSaved} />
            <View style={styles.status}>{getStatus()}</View>
            <View style={styles.solutionContainer}>
                {!solution && board && (<BoardRenderer board={board} currentGoal={currentGoal} setGoal={setGoal} />)}
                {!board && picture && (<Image style={styles.solution} source={picture} contentFit={"contain"}></Image>)}
                {solution && (<BoardRenderer board={board} currentGoal={currentGoal} solution={solution} />)}
            </View>

        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        ...StyleSheet.absoluteFill,
        flex: 1,
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