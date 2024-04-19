import { Camera, CameraType, takePictureAsync } from 'expo-camera';
import React, { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, useWindowDimensions } from 'react-native';
import { Image } from 'expo-image';
import { manipulateAsync, FlipType, SaveFormat } from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';
import { Svg, Defs, Pattern, Path, Rect, Ellipse, Line, G } from 'react-native-svg';

const BoardRenderer = ({ board, currentGoal, setGoal }) => {
    const chunkSize = 32;
    const { walls, robots, goals = null } = board;
    const wall = walls[0];

    const renderWall = (wall) => {
        return (
            <Line key={JSON.stringify(wall)} x1={chunkSize * Math.ceil(wall[1])} y1={chunkSize * Math.ceil(wall[0])} x2={chunkSize * (Math.floor(wall[1]) + 1)} y2={chunkSize * (Math.floor(wall[0]) + 1)} stroke="black" strokeWidth="5" />
        )
    };

    const renderGoal = ([goal, [x, y]]) => {
        const Types = {
            "c": "M 16,16 m 8,0 a 8,8 0 1,0 -16,0 a 8,8 0 1,0 16,0",
            "t": "M 16 8 L 24 24 8 24 16 8",
            "h": "M 12 8 L 20 8 25 16 20 24 12 24 7 16 12 8",
            "s": "M 8 8 L 24 8 24 24 8 24 8 8"
        }
        const colors = {
            "r": "red",
            "g": "green",
            "b": "blue",
            "y": "yellow",
            "m": "grey"
        }
        const alpha = (!currentGoal || currentGoal == goal) ? 1 : 0.2;
        return (
            <G
                key={goal}
            >
                <Path
                    d={Types[goal[1]]}
                    fill={colors[goal[0]]}
                    fillOpacity={alpha}
                    strokeOpacity={alpha}
                    stroke={"black"}
                    strokeWidth="1"
                    x={chunkSize * y}
                    y={chunkSize * x}
                />
                <Rect
                    fill={"transparent"}
                    onPress={() => { setGoal(goal) }}
                    width={32}
                    height={32}
                    x={chunkSize * y}
                    y={chunkSize * x}
                ></Rect>
            </G>
        );
    };

    const renderRobot = ([color, [x, y]]) => {
        return (
            <Rect
                key={color}
                fill={color}
                x={chunkSize * y}
                y={chunkSize * x}
                width={chunkSize}
                height={chunkSize}
            />
        );
    }


    return (
        <View style={styles.container}>
            <Svg width="80%" height="100%" viewBox="0 0 512 512">
                <Defs>
                    <Pattern
                        id="grid"
                        patternUnits="userSpaceOnUse"
                        x="0"
                        y="0"
                        width="32"
                        height="32">
                        <Path d="M 0 0 L 32 0 32 32 0 32 0 0" fill="transparent" stroke="black" strokeWidth="1" />
                    </Pattern>
                </Defs>
                {Object.entries(robots).map(renderRobot)}
                {walls.map(renderWall)}
                <Rect fill="url(#grid)" x="0" y="0" width="512" height="512"/>
                <Path d="M 0 0 L 512 0 512 512 0 512 0 0" fill="none" stroke="black" strokeWidth="5" onPress={() => setGoal(null)} />
                {Object.entries(goals).map(renderGoal)}
            </Svg>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'space-between',
        alignItems: 'center',
        ...StyleSheet.absoluteFill,
    }
});

export { BoardRenderer };