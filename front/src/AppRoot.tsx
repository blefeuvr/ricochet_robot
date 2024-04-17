import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { BoardReader } from './screens/BoardReader';
import { Solution } from './screens/Solution';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
        <View style={{ flex: 1 }}>
            <Stack.Navigator screenOptions={{ headerShown: false }}>
              <Stack.Screen name="BoardReader" component={BoardReader} />
              <Stack.Screen name="Solution" component={Solution} />
            </Stack.Navigator>
          </View>
    </NavigationContainer>
  );
}
