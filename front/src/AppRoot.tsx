import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View } from "react-native";
import { BoardReader } from "./screens/BoardReader";

export default function App() {
  return (
    <View style={{ flex: 1 }}>
      <BoardReader />
      <StatusBar translucent />
    </View>
  );
}
