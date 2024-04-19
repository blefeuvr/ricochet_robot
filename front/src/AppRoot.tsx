import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { BoardReader } from './screens/BoardReader';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <BoardReader/>
  );
}
