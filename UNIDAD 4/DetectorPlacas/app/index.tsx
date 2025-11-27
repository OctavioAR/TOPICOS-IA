import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Link } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
// pantalla de inicio 
export default function pantallaInicial() {
  return (
    // componente principal con estilos
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Detector de Placas</Text>
        <Text style={styles.subtitle}>
          Bienvenido al sistema de detección de matrículas vehiculares.
        </Text>
      </View>

      <View style={styles.instructionsContainer}>
        <Text style={styles.instructionsTitle}>Instrucciones de Uso:</Text>
        <View style={styles.instructionItem}>
          <Ionicons name="camera-outline" size={24} color="#000000ff" style={styles.icon} />
          <Text style={styles.instructionText}>
            Presione &quot;Iniciar&quot; para abrir la cámara.
          </Text>
        </View>
        <View style={styles.instructionItem}>
          <Ionicons name="scan-outline" size={24} color="#000000ff" style={styles.icon} />
          <Text style={styles.instructionText}>
            Enfoque la placa del vehículo de forma clara y centrada.
          </Text>
        </View>
        <View style={styles.instructionItem}>
          <Ionicons name="sunny-outline" size={24} color="#000000ff" style={styles.icon} />
          <Text style={styles.instructionText}>
            Asegure buena iluminación y evite reflejos.
          </Text>
        </View>
        <View style={styles.instructionItem}>
          <Ionicons name="checkmark-circle-outline" size={24} color="#000000ff" style={styles.icon} />
          <Text style={styles.instructionText}>
            El sistema procesará la imagen y mostrará los resultados.
          </Text>
        </View>
      </View>
      
      <Link href="/(tabs)/camara" asChild>
        <TouchableOpacity style={styles.startButton}>
          <Text style={styles.startButtonText}>Iniciar</Text>
        </TouchableOpacity>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffffff',
    justifyContent: 'space-around',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    alignItems: 'center',
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#000000ff',
    marginTop: 16,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#000000ff',
    textAlign: 'center',
    marginTop: 30,
  },
  instructionsContainer: {
    width: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.1)',
    borderRadius: 10,
    padding: 20,
  },
  instructionsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000000ff',
    marginBottom: 15,
    textAlign: 'center',
  },
  instructionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  icon: {
    marginRight: 15,
  },
  instructionText: {
    fontSize: 16,
    color: '#000000ff',
    flex: 1,
  },
  startButton: {
    backgroundColor: '#4caf50',
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 30,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 5,
  },
  startButtonText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginRight: 10,
  },
});