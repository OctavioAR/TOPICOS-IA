import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  Button,
  Image,
  ActivityIndicator,
  Alert,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Camera, CameraView } from 'expo-camera';
import * as ImageManipulator from 'expo-image-manipulator';
import { Ionicons } from '@expo/vector-icons';

// definimos las interfaces de tiposa de los datos recibidos
interface Deteccion {
  placa: string;
  confianza: number;
  bbox: number[];
  indice: number;
  datos_vehiculo?: FirebaseVehicleData;
  placa_ocr_original?: string;
  corregido_por_db?: boolean;
}

interface PropietarioData {
  id: string;
  nombre?: string;
  contacto?: string;
  telefono?: string;
}

interface FirebaseVehicleData {
  matricula?: string;
  marca?: string;
  modelo?: string;
  color?: string;
  año?: number;
  propietario_id?: string;
  propietario?: PropietarioData | null;
}

interface ApiResponse {
  estado: string;
  placa: string;
  confianza: number;
  bbox: number[];
  todas_detecciones: Deteccion[];
  datos_vehiculo?: FirebaseVehicleData | null;
  mensaje?: string;
}

//declaramos la url de la api, la cual se debe de cambiar dependiento de la IP local
const apiURL = 'http://192.168.1.13:8000/detectar-placa'; 

// expresiones regulares para validar placas comunes
const expresionesRegulares = [
  /^[A-Z]{3}-?\d{2}-?\d{2}$/,     
  /^[A-Z]{3}\d{3,5}$/,             
  /^[A-Z]{2}\d{4,5}$/,             
  /^\d{3,4}[A-Z]{3}$/,             
  /^[A-Z]{3}\d{3}[A-Z]$/,           
  /^[A-Z]{2,3}\d{2,5}$/,           
  /^[A-Z]\d{2}[A-Z]{3}$/,           
];

//validamos que una placa sea valida 
function esPlacaValida(placa: string): boolean {
  if (!placa || placa.length < 5 || placa.length > 12) {
    return false;
  }
  // limpiamos la placa de espacions y guiones
  const limpia = placa.replace(/[-\s]/g, '').toUpperCase();
  const tieneLetras = /[A-Z]/.test(limpia);
  const tieneNumeros = /\d/.test(limpia);
  
  if (!tieneLetras || !tieneNumeros) {
    return false;
  }
  // patron general para placas comunes
  const patronGeneral = /^[A-Z]{2,3}\d{3,5}$|^\d{3,4}[A-Z]{2,3}$|^[A-Z]{3}\d{3}[A-Z]$|^[A-Z]\d{2}[A-Z]{3}$/;
  if (patronGeneral.test(limpia)) {
    return true;
  }
  // retorna true si alguna de las expreciones regulares coincide
  return expresionesRegulares.some(patron => patron.test(limpia));
}

//validamos que una placa sea basura
function esPlacaBasura(placa: string): boolean {
  const limpia = placa.replace(/[-\s]/g, '').toUpperCase();
  // se concidera basura si tiene solo letras o numeros o patrones repetitivos
  const patronesBasura = [
    /^[A-Z]{6,}$/,           
    /^\d{6,}$/,              
    /^[A-Z]+\d{1,2}$/,       
    /^(.)\1{4,}/,            
    /^[A-Z]{1,2}\d{6,}$/,    
  ];
  
  return patronesBasura.some(patron => patron.test(limpia));
}
// componente principal de la pantalla de camara
export default function HomeScreen() {
  //estados del componente
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [photo, setFoto] = useState<string | null>(null);
  const [isLoading, cargando] = useState(false);
  const [vehicleData, datosVehiculo] = useState<ApiResponse | null>(null);
  const [mostrarError, setMostrarError] = useState(false);
  
  const cameraRef = useRef<CameraView | null>(null); 

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);
  // funcion para enviar la imagen a la api
  const enviarImgApi = async (uri: string) => {
    cargando(true);
    datosVehiculo(null);
    setMostrarError(false);
    
    try {
      // redimensionamos y comprimimos la imagen
      const manip = await ImageManipulator.manipulateAsync(
        uri,
        [{ resize: { width: 800 } }],
        { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
      );
      // preparar el form data para enviar
      const formData = new FormData();
      formData.append('imagen', {
        uri: manip.uri,
        name: 'foto.jpg',
        type: 'image/jpeg',
      } as any);
      // enviamos la imagen a la api con la peticion POST
      const resp = await fetch(apiURL, {
        method: 'POST',
        body: formData,
      });
      // procesamos la respuesta
      const data: ApiResponse = await resp.json();

      if (!resp.ok) {
        Alert.alert('Error', data.mensaje || data.estado || 'Fallo en servidor');
        setMostrarError(true);
        return;
      }

      if (data.estado === 'no_detectado') {
        Alert.alert('Sin detección', 'No se detectó ninguna placa en la imagen.');
        setMostrarError(true);
        return;
      }
      
      const placaValida = esPlacaValida(data.placa);
      const placaBasura = esPlacaBasura(data.placa);
      const tieneDatosFirebase = data.datos_vehiculo && 
                                 Object.values(data.datos_vehiculo).some(v => v != null && v !== '');
      
      console.log('Validación:', {
        placa: data.placa,
        placaValida,
        placaBasura,
        tieneDatosFirebase,
        datos: data.datos_vehiculo
      });
      
      if (placaBasura && !tieneDatosFirebase) {
        console.log('Rechazada: placa basura sin datos');
        Alert.alert(
          'No encontrado',
          'La matrícula no se encontró en la base de datos.\n\nPor favor, intente de nuevo.'
        );
        setMostrarError(true);
        return;
      }
      
      if (tieneDatosFirebase) {
        console.log('Aceptada: tiene datos en Firebase');
        datosVehiculo(data);
        
        Alert.alert(
          'Éxito',
          `Placa: ${data.placa}\nPropietario: ${data.datos_vehiculo?.propietario?.nombre || 'N/A'}`
        );
        return;
      }
      
      if (!placaValida) {
        console.log('Rechazada: formato inválido y sin datos');
        Alert.alert(
          'No encontrado',
          'La matrícula no se encontró en la base de datos.'
        );
        setMostrarError(true);
        return;
      }
      
      setMostrarError(true);
      Alert.alert(
        'No registrada',
        `La placa ${data.placa} tiene formato válido pero no está registrada en la base de datos.`
      );
      
    } catch (e) {
      console.error('Error enviando imagen:', e);
      Alert.alert('Error de conexión', 'No se pudo conectar con el servidor.');
      setMostrarError(true);
    } finally {
      cargando(false);
    }
  };
  // funcion para tomar la foto desde la camara
  const tomarFoto = async () => {
    if (!cameraRef.current) return;
    try {
      setFoto(null);
      datosVehiculo(null);
      setMostrarError(false);
      
      const foto = await cameraRef.current.takePictureAsync({ 
        quality: 0.7, 
        skipProcessing: true 
      });
      // si se obtuvo la foto entonces actualizar estado y enviar a la API
      if (foto?.uri) {
        setFoto(foto.uri);
        enviarImgApi(foto.uri);
      } else {
        Alert.alert('Error', 'No se obtuvo imagen.');
      }
    } catch (e) {
      console.error('Error tomando foto:', e);
      Alert.alert('Error', 'Fallo al tomar la foto.');
    }
  };

  if (hasPermission === null) {
    return <View style={styles.center}><ActivityIndicator /></View>;
  }
  // mensaje para cuando no se tiene permiso de camara al usar la app
  if (hasPermission === false) {
    return (
      <View style={styles.center}>
        <Text style={{ marginBottom: 12, fontSize: 16 }}>Sin permisos de cámara</Text>
        <Button
          title="Solicitar Permiso"
          onPress={async () => {
            const { status } = await Camera.requestCameraPermissionsAsync();
            setHasPermission(status === 'granted');
          }}
        />
      </View>
    );
  }
// etiquetas del componente 
  return (
    <View style={styles.container}>
      {!photo ? (
        <CameraView
          style={styles.camera}
          facing="back"
          ref={cameraRef}
        >
          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.captureBtn} onPress={tomarFoto}>
              <Ionicons name="camera" size={42} color="#fff" />
            </TouchableOpacity>
          </View>
        </CameraView>
      ) : (
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.previewBlock}>
            <Image source={{ uri: photo }} style={styles.photo} />
            
            <Button
              title="Nueva Foto"
              onPress={() => {
                setFoto(null);
                datosVehiculo(null);
                setMostrarError(false);
              }}
              color="#007AFF"
            />

            {isLoading && (
              <View style={styles.loading}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={{ marginTop: 8, fontSize: 16 }}>Procesando imagen...</Text>
              </View>
            )}

            {mostrarError && !isLoading && (
              <View style={styles.errorCard}>
                <Text style={styles.errorTitle}>No se encontró la matrícula</Text>
                <Text style={styles.errorMessage}>
                  La placa no está registrada en la base de datos.
                </Text>
                <Text style={styles.errorSuggestion}>
                  Sugerencias:{'\n'}
                  • Asegúrate de que la placa esté bien visible{'\n'}
                  • Mejora la iluminación{'\n'}
                  • Acerca más la cámara{'\n'}
                  • Evita reflejos o sombras
                </Text>
              </View>
            )}

            {vehicleData && !mostrarError && (
              <View style={styles.resultCard}>
                <Text style={styles.mainPlate}>{vehicleData.placa}</Text>

                {vehicleData.datos_vehiculo && (
                  <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Datos del Vehículo</Text>
                    <Text style={styles.line}>
                      Propietario: {vehicleData.datos_vehiculo.propietario?.nombre || 'N/A'}
                    </Text>
                    <Text style={styles.line}>
                      Marca: {vehicleData.datos_vehiculo.marca || 'N/A'}
                    </Text>
                    <Text style={styles.line}>
                      Año: {vehicleData.datos_vehiculo.año || 'N/A'}
                    </Text>
                    <Text style={styles.line}>
                      Modelo: {vehicleData.datos_vehiculo.modelo || 'N/A'}
                    </Text>
                    <Text style={styles.line}>
                      Color: {vehicleData.datos_vehiculo.color || 'N/A'}
                    </Text>
                  </View>
                )}
              </View>
            )}
          </View>
        </ScrollView>
      )}
    </View>
  );
}
// estilos del componente
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  camera: { flex: 1 },
  buttonRow: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 30,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureBtn: {
    backgroundColor: 'rgba(0,0,0,0.6)',
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#fff',
    alignSelf: 'center',
    marginBottom: 10,
  },
  buttonWrapper: {
    backgroundColor: 'rgba(0,0,0,0.6)',
    borderRadius: 8,
    overflow: 'hidden',
  },
  scroll: { flexGrow: 1, paddingBottom: 40 },
  previewBlock: {
    flex: 1,
    alignItems: 'center',
    paddingTop: 40,
    backgroundColor: '#fff',
  },
  photo: {
    width: '92%',
    height: 300,
    resizeMode: 'contain',
    marginBottom: 18,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 6,
  },
  loading: {
    marginTop: 20,
    alignItems: 'center',
  },
  errorCard: {
    width: '92%',
    backgroundColor: '#ffebee',
    padding: 20,
    borderRadius: 10,
    marginTop: 20,
    borderWidth: 2,
    borderColor: '#ef5350',
    alignItems: 'center',
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 10,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#c62828',
    marginBottom: 8,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: 16,
    color: '#555',
    textAlign: 'center',
    marginBottom: 12,
  },
  errorSuggestion: {
    fontSize: 14,
    color: '#666',
    textAlign: 'left',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 6,
    width: '100%',
  },
  resultCard: {
    width: '92%',
    backgroundColor: '#e8f5e9',
    padding: 16,
    borderRadius: 10,
    marginTop: 20,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#4caf50',
  },
  title: { 
    fontSize: 18, 
    fontWeight: '700', 
    textAlign: 'center', 
    marginBottom: 8, 
    color: '#2e7d32' 
  },
  mainPlate: { 
    fontSize: 32, 
    fontWeight: 'bold', 
    textAlign: 'center', 
    color: '#1b5e20', 
    marginBottom: 8,
    letterSpacing: 2,
  },
  line: { fontSize: 14, color: '#333', marginVertical: 2 },
  section: { 
    marginTop: 12, 
    paddingTop: 8, 
    borderTopWidth: 1, 
    borderTopColor: '#a5d6a7' 
  },
  sectionTitle: { 
    fontSize: 15, 
    fontWeight: '600', 
    marginBottom: 4, 
    color: '#2e7d32' 
  },
});