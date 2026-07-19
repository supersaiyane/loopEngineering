// HealthGuard Pro — Patient Mobile App (React Native)
// Sprint 2: patient portal, vitals view, alerts
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>HealthGuard Pro</Text>
      <Text style={styles.subtitle}>Patient App — Sprint 2</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 24, fontWeight: 'bold' },
  subtitle: { color: '#666', marginTop: 8 },
});
